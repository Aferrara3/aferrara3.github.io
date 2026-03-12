"""
Manual Strategy Shit
TODO stub this out for how to use it
TODO make this more extensible
"""

import numpy as np
import ML4TE.indicators as ind

def testPolicy(df_prices, symbol, threshold=0.4):

	df_prices.fillna(method = 'ffill',inplace = True)
	df_prices.fillna(method = 'backfill', inplace = True)

	# Manual Strat Here
	bbp = ind.bbp(df_prices,window=20,plot=False, plot_HD=False)
	rsi = ind.rsi(df_prices,window=14, plot=False, plot_HD=False)
	macd_h = ind.macd(df_prices,12,26,9,plot=False, plot_HD=False)

	bbp_signal 	= ((bbp * -4/3)  + 1)*2		#Need to generalize these vals from spreadsheet analysis
	rsi_signal 	= ((rsi * -0.05) + 2.5)*2	#Need to generalize these vals from spreadsheet analysis
	macd_signal = macd_h.copy()
	macd_signal[:] = 0
	macd_signal.loc[ (macd_h[symbol] >= 0) & (macd_h[symbol].shift(1) <  0) ] = 1
	macd_signal.loc[ (macd_h[symbol] <  0) & (macd_h[symbol].shift(1) >= 0) ] = -1
	#macd_signal.fillna(method = 'ffill',inplace = True)

	macd_signal.rename(columns={symbol:'MACD'}, inplace=True)
	bbp_signal.rename(columns={symbol:'BBP'}, inplace=True)
	rsi_signal.rename(columns={symbol:'RSI'}, inplace=True)

	signal_score = macd_signal.copy()
	signal_score = signal_score.join(bbp_signal, how='outer')
	signal_score = signal_score.join(rsi_signal, how='outer')

	df_trades = df_prices.copy()
	df_trades[:] = np.nan

	df_trades.loc[ signal_score.sum(axis=1) >= threshold ] = 1000
	df_trades.loc[ signal_score.sum(axis=1) <= -1*threshold ] = -1000

#	df_trades.loc[ df_prices[symbol] == df_prices[symbol].shift(-1) ] = np.NaN
#	df_trades.fillna(method = 'backfill', inplace = True) #Future peeking?

	df_trades.ffill(inplace=True)
	df_trades.fillna(0, inplace=True)
	df_trades[:] = df_trades.diff()
	df_trades.iloc[0] = 0;

	return df_trades


### Approach Pre-Planning ###
#	Normalize each indicator -1 - 1 for signal levels + potential overages
#		Planned in excel sheet on dummy data for lin regs
#	Give them a "strength" of signal relative to their threshold
#		ie RSI how much >70 or <30
#			More weight to a signal that is way out of range
#			0, or even negative! signal, if it is like 50
#	Sum that shit up for an aggregated signal strength score
#	Make the trade if the signal_score is >some threshold
#		Can vary that threshold and monitor performance change! (on in-sample data)
#	Combine the indicator results all into 1 dataframe and then can sum and check conditions and shit accross the rows
#	Can even filter it for what days have signal_scores vectorized


### TODO ###
#	Loop with different thresholds to compare	[DONE]
#	Ensure no peeking occurring					[DONE]
#	Try out mean strat							[DONE] (sucked)
#	Try out threshold /voting/ strat			[DONE]
#	Try giving indicators different weighting	[DONE]

# Things I want to do but time consuming and performance is good enough for now. Will revisit post-project
#	Also could give macd additional weight based on magnitude? Or Rising/falling not just crossovers
#		Already have the hist data anyways so easy enough to try
# 	Instead of lin reg, use expontial beyond thresholds instead for extra weight to those signals
# 	Try out partial shares strat instead of only trading 1k @ a time
