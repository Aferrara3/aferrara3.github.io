"""
24 karat indicator magic in the aaaaaaaaaaiiiiiiiirrrrrr
"""
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

def normalize(df_prices):
	df_prices.fillna(method='ffill', inplace=True)
	df_prices.fillna(method='bfill', inplace=True)
	return df_prices/df_prices.iloc[0,:]

def calc_sma(df_prices, window):
	return df_prices.rolling(window=window, min_periods = window).mean()

def calc_ema(df_prices, window):
	return df_prices.ewm(span=window,min_periods=window,adjust=False,ignore_na=False).mean()

# Will want to look for when bbp>1 (overbought), bbp<0 (oversold)
def bbp(df_prices,window=20,plot=False,plot_HD=False):
	df_prices = normalize(df_prices)
	rolling_std = df_prices.rolling(window=window, min_periods=window).std()
	sma = calc_sma(df_prices, window)
	top_band = sma + (2*rolling_std)
	bottom_band = sma - (2*rolling_std)
	bbp = (df_prices-bottom_band)/(top_band-bottom_band)

	if(plot):
		fig, ax = plt.subplots(2, 1, sharex=True)
		if(plot_HD):
			fig.set_dpi(600)
		plt.xlabel("Date")
		ax[0].set_title('Bollinger Bands')
		ax[0].set(ylabel='Normalized Price')
		ax[0].grid(axis='both', linestyle='--')
		ax[0].plot(df_prices, label="Prices")
		ax[0].plot(sma, label="SMA")
		ax[0].plot(top_band, label="BB Top")
		ax[0].plot(bottom_band, label="BB Bottom")

		ax[1].set(ylabel='%')
		ax[1].set_title('BB%')
		ax[1].grid(axis='both', linestyle='--')
		ax[1].plot(bbp, label="BBP")
		fig.autofmt_xdate()
		fig.savefig('BBP.png')
		plt.close()

	return bbp

# Will want to look for when rsi>70 (overbought), rsi<30 (oversold)
def rsi(df_prices,window=14,plot=False, plot_HD=False):
	daily_returns = df_prices.copy()
	daily_returns[1:]=(df_prices[1:]/df_prices[:-1].values)-1
	daily_returns.iloc[0,:]=0

	up_rets = daily_returns[daily_returns>=0].fillna(0).cumsum()
	down_rets = -1 * daily_returns[daily_returns<0].fillna(0).cumsum()

	up_gain = df_prices.copy()
	up_gain.iloc[:,:] = 0
	up_gain.values[window:,:] = up_rets.values[window:,:] - up_rets.values[:-window,:]

	down_loss = df_prices.copy()
	down_loss.iloc[:,:] = 0
	down_loss.values[window:,:] = down_rets.values[window:,:] - down_rets.values[:-window,:]

	rs = (up_gain / window) / (down_loss / window)
	rsi = 100 - (100 / (1+rs))
	rsi.iloc[:window,:] = np.nan

	rsi[rsi == np.inf] = 100

	if(plot):
		sma = calc_sma(df_prices, window) # 1 day sma for chart
		fig, ax = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1]})
		if(plot_HD):
			fig.set_dpi(600)
		plt.xlabel("Date")
		ax[0].set_title('Price')
		ax[0].set(ylabel='Price ($)')
		ax[0].grid(axis='both', linestyle='--')
		ax[0].plot(df_prices, label="Prices")
		ax[0].plot(sma, label="SMA")

		ax[1].set(ylabel='RSI')
		ax[1].set_title('RSI')
		ax[1].grid(axis='both', linestyle='--')

		y30 = rsi.copy()
		y30.iloc[:,:] = 30
		y70 = rsi.copy()
		y70.iloc[:,:] = 70
		ax[1].plot(y30)
		ax[1].plot(y70)
		ax[1].plot(rsi, label="RSI")
		fig.autofmt_xdate()
		fig.savefig('RSI.png')
		plt.close()

	return rsi

def macd(df_prices, w1=12, w2=26, w3=9, plot=False, plot_HD=False):
#MACD Line: (12-day EMA - 26-day EMA)
#Signal Line: 9-day EMA of MACD Line
#MACD Histogram: MACD Line - Signal Line
	ema12 = calc_ema(df_prices, w1)
	ema26 = calc_ema(df_prices, w2)
	macd = ema12 - ema26

	signal = calc_ema(macd, w3)
	macd_hist = macd - signal

	if(plot):
		sma = calc_sma(df_prices, w1) # 1 day sma for chart
		fig, ax = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1]})

		if(plot_HD):
			fig.set_dpi(600)

		plt.xlabel("Date")
		ax[0].set_title('Price')
		ax[0].set(ylabel='Price ($)')
		ax[0].grid(axis='both', linestyle='--')
		ax[0].plot(df_prices, label="Prices")
		ax[0].plot(sma, label="SMA")

		ax[1].set_title('MACD')
		ax[1].grid(axis='both', linestyle='--')
		ax[1].plot(macd, label="MACD")
		ax[1].plot(signal, label="Signal")
		macd_hist.fillna(0, inplace = True)
		ax[1] = plt.bar(macd_hist.index, macd_hist[macd_hist.columns[0]])
		fig.autofmt_xdate()
		fig.savefig('MACD.png')
		plt.close()

	return macd_hist


# Need to revamp to use Alpaca Util, but should keep fo sho
def test_code():
	symbols = ["JPM"]
	start_date = dt.datetime(2008, 1, 1)
	end_date = dt.datetime(2009,12,31)

	#df_prices = get_data(symbols, pd.date_range(start_date, end_date))
	df_prices = []
	# NEED TO UPDATE TO alpaca_util to use !!!

	df_prices.fillna(method = 'ffill',inplace = True)
	df_prices.fillna(method = 'backfill', inplace = True)
	df_prices.drop("SPY",axis =	 1,inplace=True)
	bbp(df_prices,window=20,plot=True, plot_HD=False)
	rsi(df_prices,window=14, plot=True, plot_HD=False)
	macd(df_prices,12,26,9,plot=True, plot_HD=False)

if __name__ == "__main__":
    test_code()
