from constants import RESOLUTION
from func_utils import get_ISO_times
import pandas as pd
import numpy as np
import time
import pandas as pd
from datetime import datetime,timedelta

from pprint import pprint

# Get relevant time periods for ISO from and to
ISO_TIMES = get_ISO_times()


# Get Candles Historical
def get_candles_historical(client, market):

  # Define output
  data = []

  # Extract historical price data for each timeframe
  for timeframe in ISO_TIMES.keys():

    # Confirm times needed
    tf_obj = ISO_TIMES[timeframe]
    from_iso = tf_obj["from_iso"]
    to_iso = tf_obj["to_iso"]

    # Protect rate limits
    time.sleep(3)

    # Get data
    candles = client.public.get_candles(
      market=market,
      resolution=RESOLUTION,
      from_iso=from_iso,
      to_iso=to_iso,
      limit=100
    )
    for candle in candles.data["candles"]:
          data.append({"datetime": candle["startedAt"],"Open":candle['open'],"High":candle['high'],'Low':candle['low'],"Close":candle['close'],'Volume': candle['usdVolume'] })

  df=pd.DataFrame(data)
  df['datetime']=df['datetime'].str.replace('.000Z','')
  df['datetime']=df['datetime'].str.replace('T',' ')
  df.set_index("datetime", inplace=True)
  df.index=pd.to_datetime(df.index)
  df=df.sort_index()
  df.Open=df.Open.astype(float)
  df.High=df.High.astype(float)
  df.Low=df.Low.astype(float)
  df.Close=df.Close.astype(float)
  df.Volume=df.Volume.astype(float)

  return df

def markets(client):
      markets_dict=client.public.get_markets()
      mkt_df=pd.DataFrame(markets_dict.data['markets'])
      return markets_dict,mkt_df
''' Columns
Index(['SUSHI-USD', 'LTC-USD', 'ALGO-USD', 'MKR-USD', 'CELO-USD', 'ICP-USD', 
       'BCH-USD', 'LINK-USD', 'DOGE-USD', 'MATIC-USD', 'COMP-USD', 'XTZ-USD',
       'YFI-USD', 'ADA-USD', 'SOL-USD', 'AAVE-USD', 'XLM-USD', 'AVAX-USD',   
       'XMR-USD', 'ATOM-USD', 'EOS-USD', 'LUNA-USD', 'ENJ-USD', 'SNX-USD',   
       'NEAR-USD', '1INCH-USD', 'ZRX-USD', 'UNI-USD', 'TRX-USD', 'DOT-USD',  
       'ETH-USD', 'CRV-USD', 'ZEC-USD', 'UMA-USD', 'RUNE-USD', 'FIL-USD',    
       'BTC-USD', 'ETC-USD'],
      dtype='object')'''     


def servertime(client):
      sevrver_time=client.public.get_time()
      sevrver_time=sevrver_time.data
      expiration=datetime.fromisoformat(sevrver_time['iso'].replace('Z',''))+timedelta(seconds=48000)
      return sevrver_time,expiration
      
def place_buy_order(client,position_id,market,Bid_price,expiration):
      place_order=client.private.create_order(
         position_id=position_id,
         market=market,
         side='BUY',
         order_type='LIMIT',
         post_only=False,
         size='1',
         price=Bid_price,
         limit_fee='0.015',
         expiration_epoch_seconds=expiration.timestamp(),
         time_in_force='GTT',
         reduce_only=False,
      )

      print(place_order.data)
    
def place_sell_order(client,position_id,market,Ask_price,expiration):
      place_order=client.private.create_order(
         position_id=position_id,
         market=market,
         side='SELL',
         order_type='LIMIT',
         post_only=False,
         size='1',
         price=Ask_price,
         limit_fee='0.015',
         expiration_epoch_seconds=expiration.timestamp(),
         time_in_force='GTT',
         reduce_only=False,
      )

      print(place_order.data)
    
def bid_ask(client,market):
      ob=client.public.get_orderbook(market=market)
      bid=ob.data['bids'][0]['price']
      ask=ob.data['asks'][0]['price']
      return bid,ask

           
# Construct market prices
def construct_market_prices(client,market):
      

  # Declare variables
  tradeable_markets = []
  markets = client.public.get_markets()

  # Find tradeable pairs
  for market in markets.data["markets"].keys():
    market_info = markets.data["markets"][market]
    if market_info["status"] == "ONLINE" and market_info["type"] == "PERPETUAL":
      tradeable_markets.append(market)

  # Set initial DateFrame
  close_prices = get_candles_historical(client, tradeable_markets[0])
  df = pd.DataFrame(close_prices)
  df.set_index("datetime", inplace=True)

  # Append other prices to DataFrame
  # You can limit the amount to loop though here to save time in development
  for market in tradeable_markets[1:]:
    close_prices_add = get_candles_historical(client, market)
    df_add = pd.DataFrame(close_prices_add)
    df_add.set_index("datetime", inplace=True)
    df = pd.merge(df, df_add, how="outer", on="datetime", copy=False)
    del df_add

  # Check any columns with NaNs
  nans = df.columns[df.isna().any()].tolist()
  if len(nans) > 0:
    print("Dropping columns: ")
    print(nans)
    df.drop(columns=nans, inplace=True)

  # Return result
  return df
