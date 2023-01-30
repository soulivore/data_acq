# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 17:25:14 2023

@author: maxwe
"""

"""
The plan so far:
Get all 48 days of market data for each stock. 
    Make sure to do it on a timer so as not to exceed 120 req/min
    This minimizes the number of https requests
        (6000 stocks) * (48 days) = 288000 requests
        (288000 requests) / (120 requests/min) = 2400 min = 40 hours
        assuming you can even request at max speed, which you probably can't
    Getting all 48 days for each ticker cuts the time down to
        (6000 requests) / (120 requests/min) = 50 min
Reformat the data as a series of pandas dataframes where
    each dataframe corresponds to a single day and contains info on every stock
    columns will have to be something like
    'AAPL_datetime', 'AAPL_open', 'AAPL_high', 'AAPL_low', etc
    https://www.geeksforgeeks.org/create-a-pandas-dataframe-from-lists/
Write each dataframe as a feather file: https://arrow.apache.org/docs/python/feather.html
"""

import time
import datetime as dt
import pandas as pd
import pyarrow.feather as feather

from common import beginning_of_day, yyyymmdd, FRAME_PERIOD
from get_market_data import get_market_data



# for looking at datetimes
DUMMY_SYMBOL = 'AAPL'

# timedelta representing a single day
ONE_DAY = dt.timedelta(1)



# first argument is the easy_client
# second argument is the symbol list
def write_data(client, symbols):
    
    print("Downloading historal data...")
    
    """
    market data will be stored in a dictionary of the following structure:
    dict[symbol]
        dict['timestamps', 'opens,' 'highs', 'lows']
            each dict contains a vector
    """
    
    # get market data for the list of symbols
    # also find the earliest date on which there is data
    market_data = {}
    first_element_today = {} # we will need this later
    date = dt.datetime.today()
    
    for symbol in symbols:
        
        frame_start = time.time() # for frame timing
        
        print("  ", symbol)
        
        timestamps, opens, highs, lows = get_market_data(client, symbol)
        
        # if data was returned
        if timestamps is not None:
        
            market_data[symbol] = {
                'timestamps': timestamps,
                'opens': opens,
                'highs': highs,
                'lows': lows
                }
            
            first_element_today[symbol] = 0
            
            first_date = beginning_of_day(market_data[symbol]['timestamps'][0])
            if first_date < date:
                date = first_date
                
        # otherwise, skip to the next symbol
        else:
            print("    ", "no data available")
            
        # throttle to frame period
        time_spent = time.time() - frame_start
        if time_spent < FRAME_PERIOD:
            time.sleep(FRAME_PERIOD - time_spent)
    
    print("  ", "First date of data:", date)
    
    print("Building and writing dataframes...")
    
    # iterate through days
    while date < market_data[DUMMY_SYMBOL]['timestamps'][-1]:
        tomorrow_date = date + ONE_DAY
        
        dfs_to_write = []
        
        # for each day, iterate through symbols in the market_data dict
        symbols_with_data = list(market_data.keys())
        for symbol in symbols_with_data:
            
            # check if the next timestamp in the data for that symbol is on this day
            # if so, there is data on this day
            next_timestamp = market_data[symbol]['timestamps'][first_element_today[symbol]]
            if date < next_timestamp and next_timestamp < tomorrow_date:
                
                # find the last timestamp on this day
                first_element_tomorrow = first_element_today[symbol] + 1
                while (first_element_tomorrow < len(market_data[symbol]['timestamps'])
                       and market_data[symbol]['timestamps'][first_element_tomorrow] < tomorrow_date):
                    first_element_tomorrow += 1
                    
                # record data
                data_today = list(zip(
                    market_data[symbol]['timestamps'][first_element_today[symbol]:first_element_tomorrow],
                    market_data[symbol]['opens'][first_element_today[symbol]:first_element_tomorrow],
                    market_data[symbol]['highs'][first_element_today[symbol]:first_element_tomorrow],
                    market_data[symbol]['lows'][first_element_today[symbol]:first_element_tomorrow]))
                df_today = pd.DataFrame(data_today, columns=[
                    'timestamps_' + symbol, 
                    'opens_' + symbol, 
                    'highs_' + symbol, 
                    'lows_' + symbol])
                
                dfs_to_write.append(df_today)
                
                # move on to the next symbol
                first_element_today[symbol] = first_element_tomorrow
            
            # otherwise, there is no data on this day
        
        # if there was data today, there will be dataframes in this list
        if len(dfs_to_write) > 0:
        
            # we now have a bunch of dataframes in a list
            # concatenate them and write a single dataframe
            df_to_write = pd.concat(dfs_to_write, axis=1)
            
            filepath = '../data/' + yyyymmdd(date)
            feather.write_feather(df_to_write, filepath)
        
        # move on to the next day
        date += ONE_DAY



from common import get_client

if __name__ == "__main__":
    
    client = get_client()
    
    symbols = ['AAPL', 'MSFT', 'JPM']
    
    write_data(client, symbols)
    
    print("Done")