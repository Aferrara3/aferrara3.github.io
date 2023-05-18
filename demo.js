var x_dat
var y_dat

var x_dat2
var y_dat2

window.addEventListener('resize', function(event) {
    reload_plot(x_dat2, y_dat2)	
}, true);

function reload_plot(x_dat, y_dat){
	var trace1 = {
	  type: "scatter",
	  mode: 'lines+markers',
  marker: {
    color: '#17BECF',
    size: 5
  },
	  name: 'Buying Power',
	  x: x_dat.map(x => new Date(x)),
	  y: y_dat.map(x => x * 1),
	  hovertemplate: '%{x|%b %Y}<br> %{y:$.2f}<extra></extra>',
	  line: {color: '#17BECF', width:2},
      
	}

	var data = [trace1];

	var height = 0.9 * (window.innerHeight - document.getElementsByTagName("div")[0].clientHeight)
	var width = 0.99 * window.innerWidth

	var layout = {
	  height: height,
	  width: width,
	  title: 'Buying Power Inflation',
	  xaxis: {
		showticklabels: true,
		tickangle: 'auto',
		tickfont: {
		  family: 'Old Standard TT, serif',
		  size: 14,
		  color: 'black'
		},
		tickformat:'%b\n%Y',
        nticks: 20,
		tickangle: 30,
		exponentformat: 'e',
		showexponent: 'all'
	  },
	  yaxis: {
		title: '$',
		titlefont: {
		  family: 'Arial, sans-serif',
		  size: 18,
		  color: 'lightgrey'
		},
	  }

	};

	Plotly.newPlot('myDiv', data, layout);	
}

function update_date(month, year){
	target_date = month+"/1/"+year
	var index = -1
	for(var i = 0; i < x_dat.length; i++) {
		if(x_dat[i] == target_date) {
			index = i;
			console.log(i)
			break;
		}
	}
	console.log(i,x_dat[i])

	var normalize_factor = y_dat[i]
	x_dat2 = x_dat.slice(i,x_dat.length)
	y_dat2 = y_dat.slice(i,y_dat.length).map(x => x / normalize_factor)
	
	reload_plot(x_dat2, y_dat2)	
}

function dateChanged(){
			var month = document.getElementById("year1-month").value
			var year = document.getElementById("year1-year").value
			
			if (month[0] == "0"){month=month[1]}
			update_date(month,year)
		}	


d3.csv("https://alexanderferrara.com/files/CPI_out.csv", function(err, rows){

  function unpack(rows, key) {
  return rows.map(function(row) { return row[key]; });
}

x_dat = unpack(rows, 'Date')
y_dat = unpack(rows, 'Value')

x_dat2 = x_dat
y_dat2 = y_dat

reload_plot(x_dat, y_dat)

});

