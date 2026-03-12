import requests_cache
import datetime
from alpaca_trade_api.rest import REST, TimeFrame
import os

def cache_init():
    # CHANGE THIS BACK TO N-HOURS #
    expire_after = datetime.timedelta(seconds=30)
    requests_cache.install_cache('stonk_data/alpaca_cache', expire_after=expire_after)
    requests_cache.remove_expired_responses()
    print("CACHE INITIALIZED!")

def test_code():
    print("alpaca_util test_code() hit")
    print("FUNCTIONALLY DISABLING CACHE FOR ML4T APP WHILE WORKING ON SBA APP. SORT OUT WHITELISTING LATER!!!")
    cache_init()
    symbol = "GM"
    df_prices = get_prices(symbol,'2017-08-01','2019-09-02', tf=TimeFrame.Day, crypto=False)
    return(df_prices)

def get_prices(symbol, sd, ed, tf, crypto=False):
    key_id = os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("APCA_API_SECRET_KEY")
    base_url = os.getenv("APCA_API_BASE_URL")
    api = REST(key_id, secret_key, base_url, api_version='v2')

    sd = str(sd).split(" ")[0]
    ed = str(ed).split(" ")[0]

    # Doing it ^ janky way because not typesafe usage somewhere... oops
    #sd = sd.strftime("%Y-%m-%d")
    #ed = ed.strftime("%Y-%m-%d")

    if not crypto:
        data = api.get_bars(symbol, tf, sd, ed, adjustment='all').df
    else:
        data = api.get_crypto_bars(symbol, tf, start=sd, end=ed, exchanges=["CBSE"]).df

    #data = index_norm_form(data)#["close"]
    #df_adj_close = pd.DataFrame({symbol: data})
    return data


def index_norm_form(df):
    # Normalize datetime index formats
    # df index -> new datetime format
    # YYYY-MM-DD hh:mm:ss
    df.index = df.index.date #pd.to_datetime(df.index, format="%y/%m/%d") # %H:%M:%S")
    return df

if __name__ == "__main__":
    test_code()