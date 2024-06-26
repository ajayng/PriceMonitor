// Function to fetch new data periodically
function fetchDataPeriodically() {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheets = spreadsheet.getSheets();
  
  sheets.forEach(function(sheet) {
    // Skip sheets that are not relevant (e.g., configuration sheets)
    if (!isDataSheet(sheet)) {
      return;
    }
    
    var newPrice = Math.random() * 1000; // Example: generate random price
    var lastRow = sheet.getLastRow();
    var timestamp = new Date();
    
    // Append new data row
    sheet.getRange(lastRow + 1, 1).setValue(timestamp);
    sheet.getRange(lastRow + 1, 2).setValue(newPrice);
    
    // Update chart after appending new data
    generatePriceGraph(sheet);
  });
}

// Function to check if a sheet is a data sheet
function isDataSheet(sheet) {
  // Example: Check if sheet name starts with "Product"
  return sheet.getName().startsWith("Product");
}

// Function to generate or update the chart
function generatePriceGraph(sheet) {
  var dataRange = sheet.getRange('A2:B'); // Assuming data starts from row 2 (headers in row 1)
  
  var charts = sheet.getCharts();
  charts.forEach(function(existingChart) {
    sheet.removeChart(existingChart);
  });
  
  var chart = sheet.newChart()
    .setChartType(Charts.ChartType.LINE)
    .addRange(dataRange)
    .setPosition(5, 5, 0, 0)
    .setOption('title', 'Price History for ' + sheet.getName())
    .setOption('hAxis', { title: 'Timestamp' })
    .setOption('vAxis', { title: 'Price (₹)' })
    .setOption('legend', { position: 'bottom' })
    .build();
  
  sheet.insertChart(chart);
}

// Trigger this function periodically (e.g., every 1 minute)
function setupTriggers() {
  ScriptApp.newTrigger('fetchDataPeriodically')
    .timeBased()
    .everyMinutes(1) // Adjust frequency as needed
    .create();
}
