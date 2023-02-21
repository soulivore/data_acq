# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 16:57:49 2023

@author: maxwe
"""

import time
import datetime as dt
import pandas as pd
import pyarrow.feather as feather

from common import yyyymmdd, FRAME_PERIOD
from get_options_data import get_options_data



# first argument is the easy_client
# second argument is the symbol list
def write_options_data(client, symbols):
    
    print("Downloading options data...")
    
    dfs = []
    
    for symbol in symbols:
        
        frame_start = time.time() # for frame timing
        
        print("  ", symbol)
        
        df = get_options_data(client, symbol)
        if df is not None:
            dfs.append(df)
        
        # throttle to frame period
        time_spent = time.time() - frame_start
        if time_spent < FRAME_PERIOD:
            time.sleep(FRAME_PERIOD - time_spent)
        
    df_all = pd.concat(dfs, ignore_index=True)
    
    print("Writing dataframe...")
    
    date = dt.datetime.today()
    filepath = '../data/' + yyyymmdd(date) + '_options'
    feather.write_feather(df_all, filepath)
    
    return df_all
    
    
  
from common import get_client  
  
if __name__ == "__main__":

    client = get_client()
    
    symbols = ['AAPL', 'MSFT', 'JPM']
    
    df = write_options_data(client, symbols)
    
    print(df)