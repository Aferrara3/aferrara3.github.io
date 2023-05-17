d3.csv("https://alexanderferrara.com/files/CPI_out.csv", function(err, rows){

  function unpack(rows, key) {
  return rows.map(function(row) { return row[key]; });
}


var trace1 = {
  type: "scatter",
  mode: "lines",
  name: 'Buying Power',
  x: unpack(rows, 'Date'),
  y: unpack(rows, 'Value'),
  line: {color: '#17BECF'}
}

var data = [trace1];

var layout = {
  title: 'Basic Time Series',
};

Plotly.newPlot('myDiv', data, layout);
})
