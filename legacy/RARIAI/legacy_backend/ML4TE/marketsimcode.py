"""
Where main organization stuff happens

inputs:
def main(	symbols = ["JPM", "AAPL", "UNH"],
				start_date_in 	= '2005-01-01',
				end_date_in 	= '2009-12-31',
				start_date_out 	= '2010-01-03', #changed for ease of out-sample
				end_date_out 	= '2011-12-31',
				commish 		=  0.0,
				impact 			=  0.000,
				sv 				=  100000,
				in_s			=  True,
				out_s			=  True,
				bins 			= 9,
				q				= True
			)

outputs:
idfky

"""

import pandas as pd
import datetime as dt
import os
from learners import StrategyLearner as sl1
import ManualStrategy as ms
import matplotlib.pyplot as plt
from alpaca_trade_api import TimeFrame as tf
from util import portfolio_util as port_util, alpaca_util as alpaca


def test_code(	symbols = ["AAPL", "JPM"],
				start_date_in 	= '2005-01-01',
				end_date_in 	= '2009-12-31',
				start_date_out 	= '2010-01-03', #changed for ease of out-sample
				end_date_out 	= '2011-12-31',
				commish 		=  0.0,
				impact 			=  0.000,
				sv 				=  100000,
				in_s			=  True,
				out_s			=  True,
				bins 			= 9,
				q				= True,
				plotting		= True,
				crypto			= False,
				timeframe		= tf.Day
			):

	# Sanitize Input Dates
	start_date_in = dt.datetime.strptime(start_date_in, '%Y-%m-%d')
	end_date_in = dt.datetime.strptime(end_date_in, '%Y-%m-%d')
	start_date_out = dt.datetime.strptime(start_date_out, '%Y-%m-%d')
	end_date_out = dt.datetime.strptime(end_date_out,'%Y-%m-%d')

	if out_s and not in_s:
		print("WARNING!! ATTEMPTING TO TEST WITHOUT TRAINING!!")

	runs = []
	if(in_s):
		runs.append("In-Sample")
	if(out_s):
		runs.append("Out-Sample")

	# Might as well handle this upfront. Some of these other files be wildin
	if not (os.path.isdir("Graphs")):
		os.makedirs("Graphs\\")

	for symbol in symbols:

		sl = None  # Placeholder for persistence outside of run in runs scope

		# Switch the order of nesting to share learner across symbols ... really that simple?
		# Would also need to change nesting of in/out sample to train all in-sample before testing any out-sample
		for run in runs:

			if run == "In-Sample":
				sd = start_date_in
				ed = end_date_in
			if run == "Out-Sample":
				sd = start_date_out
				ed = end_date_out

			results = {}
			print( "\n" + run + ": " + symbol )

			adj_close = alpaca.get_prices(symbol, sd, ed, tf=timeframe, crypto=crypto)['close']
			df_prices = pd.DataFrame({symbol:adj_close})

			# Benchmark
			results["bm"] = {}
			results["bm"]["trades"] = port_util.benchmark(df_prices, symbol)
			results["bm"]["label"] = "Benchmark"

			# Manual Strategy (TODO make the manual strategy itself customizable)
#			results["ms"] = {}
#			results["ms"]["trades"] = ms.testPolicy(df_prices, symbol)
#			results["ms"]["label"] = "Manual Strategy"

			if(run == "In-Sample"):
				# Inits fresh Q learner for each symbol. Maybe try letting it learn cross symbol in the future . . .
				sl = sl1.StrategyLearner(timeframe=timeframe, impact=impact, q=q)
				# Train
				sl.addEvidence(symbol = symbol, sd=sd, ed=ed, sv = sv, bins=bins, df_prices = df_prices)
			# Test
			results["sl"] = {}
			results["sl"]["trades"] = sl.testPolicy(symbol = symbol, sd=sd, ed=ed, sv = sv, bins=bins, df_prices = df_prices)[0]
			results["sl"]["label"] = "Strategy Learner"

			curves = []
			labels = []

			# Note "stats" aren't used rn but might become useful later
			for key in results:
				results[key]["portvals"] = port_util.compute_portvals(df_orders=results[key]["trades"], start_val=sv, commission=commish, impact=impact, df_prices = df_prices)
				results[key]["stats"] = port_util.port_stats(results[key]["portvals"], results[key]["label"])

				if (plotting):
					curves.append(results[key]["portvals"]/results[key]["portvals"][0]) #normalized curves for plotting
					labels.append(results[key]["label"])

			# Manual Enable for SL consistency check
			if(False):
				print("")
				print("")
				print("CHECK TEST POLICY CONSISTENCY")
				df_trades_s2 = sl.testPolicy(symbol = symbol, sd=start_date_in, ed=end_date_in, sv = sv,bins=bins)[0]
				df_trades_s3 = sl.testPolicy(symbol = symbol, sd=start_date_in, ed=end_date_in, sv = sv,bins=bins)[0]

				print ((df_trades_s.equals(df_trades_s2) and df_trades_s.equals(df_trades_s3)))
				print("")


				print("")

			if(plotting):
				plot_title = run + " Normalized Returns ("+symbol+")"
				n_curve_compare(
					curves = curves,
					symbol  = symbol,
					legends = labels,
					title 	= plot_title,
					xlabel	= "Date",
					ylabel	= "Normalized Cumulative Return",
					fname = "Graphs\\"+symbol+"_"+run+"_i"+str(impact)+".png"
				)

			pos_changes = results["sl"]["trades"].loc[(results["sl"]["trades"][symbol] > 0)].shape[0]
			print("Learner Position Changes: " + str(pos_changes))


def n_curve_compare(curves, legends=["label1","label2"],title="Title", xlabel="xlabel", ylabel="ylabel",plot_HD=True, fname="figure.png", trades=pd.DataFrame([]), symbol = "SYM"):
	fig, ax = plt.subplots()
	if(plot_HD):
		fig.set_dpi(600)

	colors = ['r','g','b','y','c','m','k','w']
	i = 0
	for curve in curves:
		curve.plot(color=colors[i], label=legends[i])
		i+=1
	plt.title(title)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.grid(axis='both', linestyle='--')
	ax.legend()

	if trades.shape[0]>0:
		longs = trades.loc[(trades[symbol] > 0)].index
		for xc in longs:
			ax.axvline(x=xc, color='b', linestyle='-', lw=0.3)
		shorts = trades.loc[(trades[symbol] < 0)].index
		for xc in shorts:
			ax.axvline(x=xc, color='k', linestyle='-', lw=0.3)

	fig.savefig(fname)
	plt.close()



if __name__ == "__main__":
	test_code()
