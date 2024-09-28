'''
connecting to dydx
Build a supertrend strategy for SOL --- Buy 
'''
from func_private import is_open_positions 
from datetime import datetime,timedelta
from func_connections import connect_dydx
from func_messaging import send_message
from constants import RESOLUTION
from func_utils import get_ISO_times,format_number
import pandas as pd 
from func_public import get_candles_historical,markets,servertime,place_buy_order,bid_ask,place_sell_order
from func_utils import get_ISO_times
import time
import schedule





send_message("Bot launch successful")




def supertrend(data,period=14,multipler=3):
      data['PC']=data['Close'].shift(1)
      data['H-L']=data['High']-data['Low']
      data['H-PC']=abs(data['High']-data['PC'])
      data['L-PC']=abs(data['Low']-data['PC'])
      data['TR']=data[['H-L','H-PC','L-PC']].max(axis=1)
      data['ATR']=data['TR'].rolling(period).mean()
      data['Basic_Up_band']=(data['High']+data['Low'])/2+(multipler*data['ATR'])
      data['Basic_Lw_band']=(data['High']+data['Low'])/2-(multipler*data['ATR'])
      data['up_trend']=True
      for current in range(1,len(data)):
            previous=current-1
            if data['Close'][current]>data['Basic_Up_band'][previous]:
                  data['up_trend'][current]=True
            elif data['Close'][current]<data['Basic_Lw_band'][previous]:
                  data['up_trend'][current]=False
            else:
                  data['up_trend'][current]=data['up_trend'][previous]
                  if data['up_trend'][current] and data['Basic_Lw_band'][current] < data['Basic_Lw_band'][previous]:
                        data['Basic_Lw_band'][current]=data['Basic_Lw_band'][previous]
                  if not data['up_trend'][current] and data['Basic_Up_band'][current]>data['Basic_Up_band'][previous]:
                        data['Basic_Up_band'][current]=data['Basic_Up_band'][previous]
                        
                
      return data


def bot():
      client = connect_dydx()
      acc_resp=client.private.get_account()
      position_id=acc_resp.data['account']['positionId']
      print(position_id)
      market='AVAX-USD'
      ISO_TIMES = get_ISO_times()
      ordersize=1
      pos_info=is_open_positions(client,market)
      try:
           print(pos_info)
           pos_info[0]==True
           market=pos_info[1]
           side=pos_info[2]
          
           size=pos_info[3]
           entry_price=float(pos_info[4])
           unrealizedPnl=float(pos_info[5])
           bid_price=bid_ask(client,market)[0]
           current_bid_price=float(bid_price)
           Ask_price=bid_ask(client,market)[1]
           current_ask_price=float(Ask_price)
           candle=get_candles_historical(client, market)
           supertrend(candle)
           candle['MA_200']=candle['Close'].rolling(200).mean()
           print(candle)
           sever_time=servertime(client)[0]
           expiration=servertime(client)[1]
           if side=='LONG':
                # Check PNL for the Long trade
                ret =(current_bid_price-entry_price)/entry_price
                print(ret)
                if ret < -0.1:
                      place_sell_order(client,position_id,market,Ask_price,expiration)
                else:
                      if candle['Close'][-1]>candle['MA_200'][-1]:
                            if candle['up_trend'][-1]==False:
                                  place_sell_order(client,position_id,market,Ask_price,expiration)
                            else:
                                  print('Keep the position')
                      elif candle['Close'][-1]<candle['MA_200'][-1]:
                            print('closed the position')
                            place_sell_order(client,position_id,market,Ask_price,expiration)
                            print('Just closed the position')
                      else:
                            print('Keep the position')
           if side=='SHORT':
                ret=(entry_price-current_ask_price)/entry_price
                if ret<-0.1:
                      place_buy_order(client,position_id,market,Bid_price,expiration)
                else:
                      if candle['Close'][-1]<candle['MA_200'][-1]:
                            if candle['up_trend'][-1]==True:
                                  place_buy_order(client,position_id,market,Bid_price,expiration)
                            else:
                                  print('Keep the position')
                      if candle['Close'][-1]>candle['MA_200'][-1]:
                            place_buy_order(client,position_id,market,Bid_price,expiration)
                      else:
                        print('Keep the position')

           send_message(f'My account unrealized PNL is {unrealizedPnl}')
      except:
            print(pos_info)
      time.sleep(30)
      pos_info=is_open_positions(client,market)
      try: 
            len(pos_info)
            print('position is still exixt')
      except:
            print("Fetching market prices")
            # Extract market data
            candle=get_candles_historical(client,market)
            #calulate the supertrend
            supertrend(candle)
            candle['MA_200']=candle['Close'].rolling(200).mean()
            print(candle)
            sever_time=servertime(client)[0]
            expiration=servertime(client)[1]
            if candle['Close'][-1]>candle['MA_200'][-1]:
                  if candle['up_trend'][-1]==True:
                        Bid_price=bid_ask(client,market)[0]
                        place_buy_order(client,position_id,market,Bid_price,expiration)
                  else:
                      print('There is no signal for Long the coins')
            if candle['Close'][-1]<candle['MA_200'][-1]:
                  if candle['up_trend'][-1]==False:
                        Ask_price=bid_ask(client,market)[1]
                        place_sell_order(client,position_id,market,Ask_price,expiration)
                  else:
                      print('There is no signal for Short the coins')
            else:
                  print('Wait for 5 mins to see')
      
      time.sleep(300)
      client.private.cancel_all_orders()

      # Cancel previous order
      '''try:
            client.private.cancel_all_orders()
      except:
            print('No order existed or the order has already excuted')'''

schedule.every(28).seconds.do(bot)



while True:
      schedule.run_pending()
      time.sleep(2)



''''while True:
    try:
        schedule.run_pending()
    except:
        print('+++++ MAYBE AN INTERNET PROB OR SOMETHING')
        time.sleep(30)'''
    



            
      













      










