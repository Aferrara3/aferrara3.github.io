"""
This will be the main file for testing workflows and shit
"""
import sys
import marketsimcode as mksim
from alpaca_trade_api import TimeFrame as tm

if __name__ == "__main__":
	symbols=["BTCUSD", "ETHUSD"]
	bins = 9
	if (len(sys.argv) > 1):
		symbols = [sys.argv[1]]
	if (len(sys.argv) > 2):
		bins = int(sys.argv[2])

	mksim.test_code(symbols = symbols,
					out_s = True,
					start_date_in 	= '2018-01-01',
					end_date_in 	= '2021-01-01',
					start_date_out 	= '2021-04-03', #changed for ease of out-sample
					end_date_out 	= '2022-04-04',
					timeframe		= tm.Day,
					bins 			= bins,
					q				= True,
					crypto			= True,
					sv 				= 100000
					)
