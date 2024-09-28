from datetime import datetime, timedelta
from func_utils import format_number
import pandas as pd
import time
import json

from pprint import pprint

def is_open_positions(client, market):
    
  # Get positions
  all_positions = client.private.get_positions(
    market=market,
    status="OPEN"
  )

  # Determine if open
  if len(all_positions.data["positions"]) > 0:
        open_position_info=all_positions.data["positions"][0]
        print(open_position_info)
        #market=open_position_info['market']
        side=open_position_info['side']
        size=open_position_info['size']
        entryPrice=open_position_info['entryPrice']
        unrealizedPnl=open_position_info['unrealizedPnl']

        ''''data=[]
        for position in open_position_info:
              data.append({
                  'market':position['market'],
                  'side':position['side'],
                  'size': position['size'],
                  'entryPrice':position['entryPrice'],
                  'unrealizedPnl':position['unrealizedPnl']

              })
              df=pd.DataFrame(data)'''
        return True,market,side,size,entryPrice,unrealizedPnl
  else:
    print('There is no open position')