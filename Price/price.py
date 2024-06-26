from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import logging
from time import sleep
from threading import Thread
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Twilio credentials (replace with your own)
account_sid = 'AC05136ad9c326713a1cf44ead0277afb0'
auth_token = '4134f029a1005475f408a2aa8af8cbbf'
twilio_phone_number = '+14155238886'
destination_phone_number = '+917002743716'

# Initialize Twilio client
client = Client(account_sid, auth_token)

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = '1PRIZwO6eG3aZtniP8AY_7ZCa5B0HxuJKb3EOi2leNUU'  # Replace with your Google Sheet ID

def google_sheets_service():
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def generate_sheet_name(product_url):
    try:
        page_content = fetch_product_page(product_url)
        soup = BeautifulSoup(page_content, 'html.parser')
        name_tag = soup.find('span', class_='VU-ZEz')

        # Ensure name_tag is not None before accessing its text attribute
        if name_tag:
            sheet_name = name_tag.text[:10]  # Get the first 10 characters
        else:
            sheet_name = "Unknown"  # Default name if tag is not found

    except Exception as e:
        logging.error(f"Error extracting the product name: {e}")
        sheet_name = "Error"  # Default name on error

    return sheet_name

def append_to_google_sheet(product_url, timestamp, price):
    service = google_sheets_service()
    sheet = service.spreadsheets()
    sheet_name = generate_sheet_name(product_url)

    # Check if the sheet for the product exists, create if not
    sheet_metadata = sheet.get(spreadsheetId=SHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', '')
    sheet_titles = [s['properties']['title'] for s in sheets]

    if sheet_name not in sheet_titles:
        requests = [
            {
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            }
        ]
        body = {
            'requests': requests
        }
        sheet.batchUpdate(spreadsheetId=SHEET_ID, body=body).execute()
        header_values = [['Timestamp', 'Current Price']]
        body = {
            'values': header_values
        }
        range_ = f"{sheet_name}!A1:B1"
        sheet.values().append(
            spreadsheetId=SHEET_ID,
            range=range_,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

    # Append the data
    range_ = f"{sheet_name}!A:B"
    body = {
        'values': [[timestamp, price]]
    }
    request = sheet.values().append(
        spreadsheetId=SHEET_ID,
        range=range_,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body
    )
    response = request.execute()
    logging.info(f"Google Sheets API response: {response}")

def fetch_product_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching the product page: {e}")
        return None

def extract_price(page_content, class_name):
    try:
        soup = BeautifulSoup(page_content, 'html.parser')
        price_tag = soup.find(class_=class_name)
        if price_tag:
            price = price_tag.text.replace('₹', '').replace(',', '').strip()
            return float(price)
    except Exception as e:
        logging.error(f"Error extracting the price: {e}")
    return None

def send_whatsapp_message(message):
    try:
        message = client.messages.create(
            body=message,
            from_='whatsapp:' + twilio_phone_number,
            to='whatsapp:' + destination_phone_number
        )
        logging.info(f"WhatsApp message sent successfully. SID: {message.sid}")
    except Exception as e:
        logging.error(f"Error sending WhatsApp message: {e}")

def check_price_and_alert(product_url, target_price, class_name):
    page_content = fetch_product_page(product_url)
    if page_content is None:
        logging.error(f"Failed to fetch product page for {product_url}. Exiting function.")
        return False

    current_price = extract_price(page_content, class_name)
    if current_price is None:
        logging.error(f"Failed to extract price from {product_url}. Exiting function.")
        return False

    logging.info(f"Current price for {product_url}: ₹{current_price}")

    # Log the current price with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    append_to_google_sheet(product_url, timestamp, current_price)

    if current_price <= target_price:
        message = f"Price alert! Price for {product_url} has reached the target price of ₹{target_price}. Current price is ₹{current_price}."
        logging.info(f"Sending WhatsApp message: {message}")  # Log the message before sending
        send_whatsapp_message(message)
        return True

    return False

def monitor_prices(products):
    try:
        while True:
            for product_url, (target_price, class_name) in products.items():
                if check_price_and_alert(product_url, target_price, class_name):
                    logging.info(f"Price alert condition met for product: {product_url}")
                else:
                    logging.info(f"Price alert condition not met for product: {product_url}")
            sleep(10)  # Check every 6 hours (21600 seconds)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    products = {}
    for key, value in data.items():
        if 'url' in key:
            product_id = key.replace('url', '')
            target_price_key = f'price{product_id}'
            class_name_key = f'class_name{product_id}'
            if target_price_key in data and class_name_key in data:
                products[value] = (float(data[target_price_key]), data[class_name_key])
    logging.info(f"Received products: {products}")

    thread = Thread(target=monitor_prices, args=(products,))
    thread.start()

    return jsonify({'status': 'success', 'message': 'Products submitted successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
