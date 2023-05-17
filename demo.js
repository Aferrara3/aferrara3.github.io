var x_dat
var y_dat

function reload_plot(x_dat, y_dat){
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
}


d3.csv("https://alexanderferrara.com/files/CPI_out.csv", function(err, rows){

  function unpack(rows, key) {
  return rows.map(function(row) { return row[key]; });
}

x_dat = unpack(rows, 'Date')
y_dat = unpack(rows, 'Value')

reload_plot(x_dat, y_dat)

});


target_date = "4/1/1925"
var index = -1
for(var i = 0; i < x_dat.length; i++) {
    if(x_dat[i] == target_date) {
        index = i;
        console.log(i)
        break;
    }
}
console.log(i,x_dat[i])

normalize_factor = y_dat[i]
x_dat2 = x_dat.slice(i,x_dat.length)
y_dat2 = y_dat.slice(i,y_dat.length).map(x => x / normalize_factor)
