"""
Template for implementing StrategyLearner  (c) 2016 Tucker Balch

Copyright 2018, Georgia Institute of Technology (Georgia Tech)
Atlanta, Georgia 30332
All Rights Reserved

Template code for CS 4646/7646

Georgia Tech asserts copyright ownership of this template and all derivative
works, including solutions to the projects assigned in this course. Students
and other users of this template code are advised not to share it with others
or to make it available on publicly viewable websites including repositories
such as github and gitlab.  This copyright statement should not be removed
or edited.

We do grant permission to share solutions privately with non-students such
as potential employers. However, sharing with other current or future
students of CS 7646 is prohibited and subject to being investigated as a
GT honor code violation.

-----do not edit anything above this line---

Student Name: Alexander Ferrara
GT User ID: aferrara3
GT ID: 902890849
"""

import pandas as pd
import numpy as np
import ML4TE.indicators as ind
from util import alpaca_util as utv2
from ML4TE.learners import RTLearner as rt, QLearner as ql, BagLearner as bl
from scipy import stats
from datetime import datetime, timedelta
from alpaca_trade_api import TimeFrame

class StrategyLearner(object):

	# constructor
	def __init__(self, timeframe, verbose = False, impact=0.0, q=True):
		self.verbose = verbose
		self.impact = impact
		self.learner = []
		utv2.cache_init()
		self.q = True
		self.tf = timeframe

	def discretize(self, dfi, bins=5):
		df = dfi.copy()
		colName = df.columns[0]
		df.iloc[:,df.columns.get_loc(colName)] = pd.DataFrame(pd.qcut(df.T.loc[colName], bins, labels=False))
		return df

	def colRename(self, dfs=[], names=["RSI","BBP","MACD"]):
		i=0
		for df in dfs:
			df.columns = [names[i]]
			i+=1

	# this method should create a QLearner, and train it for trading
	def addEvidence(self, symbol = "IBM", \
		sd='1/1/2008', \
		ed='1/1/2009', \
		sv = 10000,
		q = True,
		bins = 9,
		df_prices = pd.DataFrame([])):

		return self.reusable(symbol,sd,ed,sv,learning=True, bins=bins,df_prices=df_prices)

	def reusable(self, symbol = "IBM", \
		sd='1/1/2008', \
		ed='1/1/2009', \
		sv = 10000,
		learning = False,
		q = True,
		bins = 9,
		df_prices = pd.DataFrame([])):

		# example usage of the old backward compatible util function
#		syms=[symbol]
#		dates = pd.date_range(sd, ed)
#		prices_all = ut.get_data(syms, dates)  # automatically adds SPY
#		df_prices = prices_all[syms]  # only portfolio symbols
		#prices_SPY = prices_all['SPY']  # only SPY, for comparison later
		#prices.drop('SPY',axis = 1,inplace=True)

		#adj_close = utv2.get_prices(symbol,sd,ed)['close']
		#df_prices = pd.DataFrame({symbol:adj_close})

#		print(df_prices)
#		export_csv = df_prices.to_csv (r'prices2.csv', header=True)

		if self.verbose: print(df_prices)

		# example use with new colname
#		volume_all = ut.get_data(syms, dates, colname = "Volume")  # automatically adds SPY
#		volume = volume_all[syms]  # only portfolio symbols
#		volume_SPY = volume_all['SPY']  # only SPY, for comparison later
#		if self.verbose: print volume


		# I am so dumb. Why didn't I make the optimized threshold dynamic based on the existing stock data thus far for manual strat *facepalm*
		# That would be so manually feasible nothing special damn I am dumb.


		# TODO pad start date to reflect earlier data required for indicators
		sd_str = sd.strftime("%Y-%m-%d")
		ed_str = ed.strftime("%Y-%m-%d")

		padding = 0
		if self.tf.value == "1Day":
			padding = timedelta(days=30)
		elif self.tf.value == "1Hour":
			padding = timedelta(hours=30)
		elif self.tf.value == "1Min":
			padding = timedelta(minutes=30)
		sd_padded =  sd - padding

		# Janky idr why I was doing this, TODO investigate later
		sd_padded = datetime.strptime(sd_padded.strftime("%Y-%m-%d"), "%Y-%m-%d")

		adj_close = utv2.get_prices(symbol,sd_padded,ed,self.tf, crypto=False)['close']
		df_prices_padded = pd.DataFrame({symbol:adj_close})

		# END TODO

		# Be sure to drop padded start tho after generating indicators
		# Didn't do that for ManualStrategy, so seems unfair to compare as such now. Will implement post-project 8
		rsi  = ind.rsi(df_prices_padded.copy()).dropna(how='any')[sd_str:ed_str]
		bbp  = ind.bbp(df_prices_padded.copy()).dropna(how='any')[sd_str:ed_str]
		macd = ind.macd(df_prices_padded.copy()).dropna(how='any')[sd_str:ed_str]
		self.colRename([rsi, bbp, macd], ["RSI","BBP","MACD"])
		print("")
		#q = False
		if self.q:
			if(learning):
				print("Q Learning")
			else:
				print("Q Testing")
			#Discritize indicators
			# Lower better WITH impact OUT of sample . . .
			# Higher better WITHOUT impact OUT of sample & ALWAYS IN sample
			disc_cnt = bins
			rsi_disc = self.discretize(rsi, disc_cnt)
			bbp_disc = self.discretize(bbp, disc_cnt)
			macd_disc = self.discretize(macd, disc_cnt)

			self.colRename([rsi_disc,bbp_disc,macd_disc],["RSI","BBP","MACD"])

			df_indicators = pd.concat([rsi_disc, bbp_disc, macd_disc], axis = 1)
			df_indicators = df_indicators.dropna(how='any').astype("int")

			df_prices2 = pd.concat([df_prices, df_indicators], axis = 1)
			df_prices2 = df_prices2.dropna(how='any')
			df_prices2.drop(['RSI','MACD','BBP'],axis = 1,inplace=True)

#			wombo_combo = (df_indicators['RSI'].astype(str)+df_indicators['BBP'].astype(str)+df_indicators['MACD'].astype(str)).astype("int")
			wombo_combo = (df_indicators['RSI']%disc_cnt + (df_indicators['BBP']%disc_cnt)*disc_cnt + (df_indicators['MACD']%disc_cnt)*disc_cnt**2).astype("int")# 	(2%n) + ((1%n) * n) + ((0%n) * n**2)
			#wombo_combo = (df_indicators['BBP']%disc_cnt + (df_indicators['MACD']%disc_cnt)*disc_cnt).astype("int")
			#Q Stuff
#			num_states = int((str(disc_cnt)+str(disc_cnt)+str(disc_cnt)))+1
			num_states = disc_cnt ** 3
			# I wonder if I could use an optimizer to optimize each of these values for in sample data. But that'd mad overfit, no?

			if (self.learner == []):
				self.learner = ql.QLearner(num_states=num_states,\
					num_actions = 2, \
					alpha = 0.2, \
					gamma = 0.9, \
					rar = 0.99, \
					radr = 0.999, \
					dyna = 0, \
					verbose=False) #initialize the learner


			#TODO FOR QLearner post-project to actually optimize
				# Tweak every hard code value possible and see what happens
					# n day
					# lookback windows?
					# rar / radr


			converged = False
			i = 0
			j = 0
			df_trades = df_prices2.copy()
			df_trades[:] = 0
			last = df_trades.copy()
			converge_cnt = 0

			nday_rets = df_prices.copy()
			n = 5
			nday_rets[n:]=(df_prices[n:]/df_prices[:-n].values)-1
			nday_rets.iloc[n-1,:]=0
#			print nday_rets
#			print nday_rets.ix['2008-01-03']

			while not converged and j<100:
				i = 0
				x = wombo_combo[i] #discretized and concatenated!
				self.learner.querysetstate(x)
				#print df_prices.shape
				#print df_prices2.shape
				#print wombo_combo.shape
				a = 1
				for day, row in df_prices2.iterrows(): #need to make a reasonable length
					x = wombo_combo[i]
					if(learning):
						#ret = nday_rets.get_value(day, symbol) # so should be 0 for first N days, yeah? # !!! Per instructor on piazza will want Nday returns instead
						ret = nday_rets.at[day, symbol]
						#ret -= self.impact*10 #take some reward away for impact per trade
						if a == 2: #short
							r = (-1 * ret) - self.impact
						elif a == 1: #long
							r = ret - self.impact
						else: #hold
							r = 0
						a = self.learner.query(x,r)
					else:
						a = self.learner.querysetstate(x)
					#df_trades.set_value(day, symbol, a)
					df_trades.at[day, symbol] = a
					i += 1
#					print "j,i:, ",j,",",i
				j += 1
#				print df_trades
				diff = np.sum((df_trades-last).sum())
				last = df_trades.copy()
				if(diff == 0):
					converge_cnt += 1
				else:
					converge_cnt = 0
				converged = (converge_cnt == 5)
				if(not learning):
					converged = True
#				print j,": ",diff, converged

			df_trades.loc[ df_trades[symbol] == 0 ] = 0
			df_trades.loc[ df_trades[symbol] == 1 ] = 1
			df_trades.loc[ df_trades[symbol] == 2 ] = 0

		else: 	#RF Stuff - coming back to this as maybe better because it will always go with stronger correlated indicator...
			if(learning):
				print("RF Learning")
			else:
				print("RF Testing")
	#		Should z score before concat
			df_indicators = pd.concat([rsi, bbp, macd], axis = 1)
			df_indicators = df_indicators.dropna(how='any')
			df_prices2 = pd.concat([df_prices, df_indicators], axis = 1)
			df_prices2 = df_prices2.dropna(how='any')
			df_prices2.drop(['RSI','MACD','BBP'],axis = 1,inplace=True)

			nday_rets = df_prices2.copy()
			n = 100
			nday_rets[n:]=(df_prices2[n:]/df_prices2[:-n].values)-1
			nday_rets.ix[n-1,:]=0

	#		wombo_combo = df_indicators['RSI'].astype(str)+df_indicators['BBP'].astype(str)+df_indicators['MACD'].astype(str)
	#		trainX = #mash together indicators and maybe price, yeah? Maybe volume? For a given window since it'll be rolling?
						#no wait. that would be wrong because holding or current position should be in the state which is like X
						#need to JOIN them
						#drop future dates
	#		trainY = #daily returns

	# with this setup it will switch between indicators to classify and then predY will be predicted return for that day so long/short if 0<preY<0
	#	tough spot here is that it may way overtrade chasing small daily returns but commission could fuck that up
	#	need to account for impact in the reward part! Like reduce the reward by the impact somehow?
	#	can it use a threshold? If so how can that be determined with ML? optimizer for in-sample? optimizer so far along time?
	#	Use Y = nday returns instead to reduce overtrading!!!
			if (self.learner == []):
				self.learner = bl.BagLearner(learner = rt.RTLearner, kwargs = {"leaf_size":bins}, bags = 20, boost = False, verbose = False)

			if(learning):
				# Split in-sample data so as to have a range for training and testing in the range?
				# !!!! BAD !!! NEED TO USE FUTURE NDAY RETURNS INSTEAD FOR THIS APPROACH and drop nans
					# price[t+N]/price[t] -1
					# and then zscore _recommended_
				nday_rets = nday_rets.shift(-1*n)
				nday_rets.fillna(0, inplace=True)
				#breakpoint()
				nday_rets = nday_rets.apply(stats.zscore)
				nday_rets.loc[ nday_rets[symbol] < 0 ] = -1000
				nday_rets.loc[ nday_rets[symbol] == 0 ] = 0
				nday_rets.loc[ nday_rets[symbol] > 0 ] = 1000

				self.learner.addEvidence(df_indicators.to_numpy(),nday_rets.to_numpy())

			# Long because swapping df->np->df isn't very clean
			df_trades = nday_rets.copy().transpose()
			temp = [self.learner.query(df_indicators.to_numpy())]
			df_trades[:] = temp
			df_trades = df_trades.transpose()
			#predY = self.learner.query(df_indicators.to_numpy())
#			df_trades.loc[ df_trades[symbol] < 0 ] = -1000
#			df_trades.loc[ df_trades[symbol] == 0 ] = 0
#			df_trades.loc[ df_trades[symbol] > 0 ] = 1000
	#			print(df_indicators)
	#			print(nday_rets)

#		export_csv2 = df_trades.to_csv (r'ugh1.csv', index = None, header=True)
		df_trades.ffill(inplace=True)
		df_trades.fillna(0, inplace=True)

		#export_csv1 = df_trades.to_csv (r'ugh.csv', index = None, header=True)
		df_trades[0:1] = 0
		df_holding = df_trades.copy()
		new_pos = df_holding[-1:]

		pd.concat([df_trades[0:1], df_trades])
		df_trades[:] = df_trades.diff()
		#export_csv2 = df_trades.to_csv (r'ugh2.csv', index = None, header=True)
		#df_trades.ix[0] = 0;
#		export_csv = df_trades.to_csv (r'trades2.csv', header=True)
		return df_trades, df_holding, new_pos

	# this method should use the existing policy and test it against new data
	def testPolicy(self, symbol = "IBM", \
		sd='1/1/2009', \
		ed='1/1/2010', \
		sv = 10000,
		bins=9,
		df_prices = pd.DataFrame([])):
		return self.reusable(symbol,sd,ed,sv,learning=False,bins=bins,df_prices=df_prices)

	def author(self):
		return 'aferrara3'

if __name__=="__main__":
	print("One does not simply think up a strategy")
