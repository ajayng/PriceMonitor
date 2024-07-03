import pkg_resources

packages = ['flask', 'pandas', 'google-auth', 'google-api-python-client', 'twilio', 'requests', 'beautifulsoup4']

for package in packages:
    try:
        version = pkg_resources.get_distribution(package).version
        print(f"{package}: {version}")
    except pkg_resources.DistributionNotFound:
        print(f"{package} is not installed")

import requests
import logging

logging.basicConfig(level=logging.INFO)

def fetch_product_page(url):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    })
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.text
    except requests.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err} - Response: {response.text} - Status Code: {response.status_code}")
    except requests.RequestException as req_err:
        logging.error(f"Request error occurred: {req_err}")
    return None

# Example usage:
url = "https://example.com/product-page"
page_content = fetch_product_page(url)
if page_content:
    print("Successfully fetched the product page.")
else:
    print("Failed to fetch the product page.")
