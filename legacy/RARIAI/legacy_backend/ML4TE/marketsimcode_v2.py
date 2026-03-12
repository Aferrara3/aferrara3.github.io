import pandas as pd
import datetime as dt
import os
from ML4TE.learners import StrategyLearner as sl1
import ML4TE.ManualStrategy as ms
import matplotlib.pyplot as plt
from alpaca_trade_api import TimeFrame as tf
from util import portfolio_util as port_util, alpaca_util as alpaca
import sqlite3
import pickle

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

	fig.savefig("api/ML4T-extended//"+fname)
	plt.close()

def train_model(	symbols = ["AAPL"],
					start_date_in 	= '2018-01-01',
					end_date_in 	= '2019-12-31',
					commish 		=  0.0,
					impact 			=  0.000,
					sv 				=  100000,
					bins 			= 9,
					q				= True,
					plotting		= True,
					crypto			= False,
					timeframe		= tf.Day
				):

	# Sanitize Input Dates
	start_date_in = dt.datetime.strptime(start_date_in, '%Y-%m-%d')
	end_date_in = dt.datetime.strptime(end_date_in, '%Y-%m-%d')

	for symbol in symbols:
		sl = None  # Placeholder for persistence outside of run in runs scope
		sd = start_date_in
		ed = end_date_in
		
		adj_close = alpaca.get_prices(symbol, sd, ed, tf=timeframe, crypto=crypto)['close']
		df_prices = pd.DataFrame({symbol:adj_close})

		# TODO Make Learner Type Selectable #
		# Inits fresh Q learner for each symbol. Maybe try letting it learn cross symbol in the future . . .
		sl = sl1.StrategyLearner(timeframe=timeframe, impact=impact, q=q)
		# Train
		sl.addEvidence(symbol = symbol, sd=sd, ed=ed, sv = sv, bins=bins, df_prices = df_prices)

		# Save model blob and all metadata to db now. Current limitation 1x Stock/Model. TODO multi-stock/model support later #
		# !!! TODO: IMPLEMENT SAVE TO MDOEL DB!!! #
		model_id = db_add_model(sd, ed, symbol, bins, timeframe, sl, crypto)

		print("Model Trained")
	return (model_id, sl)

def test_model(		sl,
					symbols = ["AAPL"],
					sd 	= '2018-01-01',
					ed 	= '2019-12-31',
					commish 		=  0.0,
					impact 			=  0.000,
					sv 				=  100000,
					bins 			= 9,
					plotting		= False,
					crypto			= False,
					timeframe		= tf.Day
				):

	# TODO REQ CHECKING AGAINST MODEL METADATA FOR IN/OUT SAMPLE FOR TITLING SHIT #
	# IN?OUT SAMPLE CHECK HERE #

	# Sanitize Input Dates
	sd = dt.datetime.strptime(sd, '%Y-%m-%d')
	ed = dt.datetime.strptime(ed, '%Y-%m-%d')
	
	for symbol in symbols:
		adj_close = alpaca.get_prices(symbol, sd, ed, tf=timeframe, crypto=crypto)['close']
		df_prices = pd.DataFrame({symbol:adj_close})

		results = {}
		print( "\nPLACEHOLDER IN/OUT SAMPLE: " + symbol )
		# Benchmark
		results["bm"] = {}
		results["bm"]["trades"] = port_util.benchmark(df_prices, symbol, share_max = sv/df_prices[symbol][0])
		results["bm"]["label"] = "Benchmark"

		# Manual Strategy (TODO make the manual strategy itself customizable)
		#	results["ms"] = {}
		#	results["ms"]["trades"] = ms.testPolicy(df_prices, symbol)
		#	results["ms"]["label"] = "Manual Strategy"

		# Test Model
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

		if(plotting):
			if not (os.path.isdir("api\ML4T-extended\Graphs")):
				os.makedirs("api\ML4T-extended\Graphs\\")
			
			plot_title = "PLACEHOLDER" + " Normalized Returns ("+symbol+")"
			n_curve_compare(
				curves = curves,
				symbol  = symbol,
				legends = labels,
				title 	= plot_title,
				xlabel	= "Date",
				ylabel	= "Normalized Cumulative Return",
				fname = "Graphs\\"+symbol+"_In-Sample_i"+str(impact)+".png"
			)

		pos_changes = results["sl"]["trades"].loc[(results["sl"]["trades"][symbol] > 0)].shape[0]
		print("Learner Position Changes: " + str(pos_changes))

	# TODO return data formatting. Presumably portvals data and JS chartable data.
	return results


def db_add_model(sd, ed, symbol, bins, tf, model, crypto):
	sd_int = int(round(sd.timestamp()))
	ed_int = int(round(ed.timestamp()))
	try:
		sqliteConnection = sqlite3.connect('src/stonk_data/models.db')
		cursor = sqliteConnection.cursor()
		print("Connected to SQLite")
		sqlite_insert_blob_query = """ INSERT INTO MODELS (MODEL_ID,START_DATE,END_DATE,SYMBOL,BINS, TIMEFRAME, CRYPTO) VALUES (?, ?, ?, ?, ?, ?, ?)"""
		
		#TODO, better model identifcation
		model_id = dt.datetime.now().strftime("%m%d%Y%H%M%S")

		# Convert data into tuple format
		data_tuple = (model_id, sd, ed, symbol, bins, tf.value, crypto)
		cursor.execute(sqlite_insert_blob_query, data_tuple)
		sqliteConnection.commit()
		print("Model inserted successfully as a BLOB into a table")
		cursor.close()

		# Pickling
		with open("src/stonk_data/trained_models/"+model_id+".pickle","wb") as file_handle:
			pickle.dump(model, file_handle, pickle.HIGHEST_PROTOCOL)

	except sqlite3.Error as error:
		print("Failed to insert blob data into sqlite table", error)
	finally:
		if sqliteConnection:
			sqliteConnection.close()
			print("the sqlite connection is closed")
	
	return model_id





if __name__ == "__main__":
	model_id, sl = train_model()

	print("Testing1")
	test_model(sl)

	print("Testing2")
	# So pickling proved to work, the only thing is that it is a separate file to track and maintain... #
	# Unpickling
	with open(model_id+".pickle","rb") as file_handle:
		retrieved_data = pickle.load(file_handle)
		print(retrieved_data)

	test_model(retrieved_data)
	
