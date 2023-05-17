var x_dat
var y_dat
var wait = true

d3.csv("https://alexanderferrara.com/files/CPI_out.csv", function(err, rows){

  function unpack(rows, key) {
  return rows.map(function(row) { return row[key]; });
}

x_dat = unpack(rows, 'Date')
y_dat = unpack(rows, 'Value')

wait = false

});

while(wait){
	await new Promise(r => setTimeout(r, 500));
}

var trace1 = {
  type: "scatter",
  mode: "lines",
  name: 'Buying Power',
  x: x_dat,
  y: y_dat.map(x => x * 1),
  line: {color: '#17BECF'}
}

var data = [trace1];

var layout = {
  title: 'Basic Time Series',
};

Plotly.newPlot('myDiv', data, layout);