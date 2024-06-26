function generatePriceGraph(sheet, productId) {
  var data = sheet.getDataRange().getValues();

  // Check if there are at least two data points plus headers
  if (data.length < 2) {
    Logger.log('Not enough data points to create a chart for ' + productId);
    return;
  }

  // Get the range of the product data for the chart (Timestamp and Current Price columns)
  var startRow = 2; // Data starts from row 2 (excluding headers)
  var endRow = sheet.getLastRow();

  var range = sheet.getRange(startRow, 1, endRow - startRow + 1, 2); // Timestamp and Current Price columns

  // Remove existing chart for the product if exists
  var charts = sheet.getCharts();
  charts.forEach(existingChart => {
    sheet.removeChart(existingChart);
  });

  // Create the chart
  var chart = sheet.newChart()
    .setChartType(Charts.ChartType.LINE)
    .addRange(range)
    .setPosition(5, 5, 0, 0)
    .setOption('title', 'Price History for ' + productId)
    .setOption('hAxis', { title: 'Timestamp' })
    .setOption('vAxis', { title: 'Price (₹)' })
    .setOption('legend', { position: 'bottom' })
    .build();

  // Insert the new chart
  sheet.insertChart(chart);

  Logger.log('Chart created for product: ' + productId);
}
