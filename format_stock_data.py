# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 12:44:02 2023

@author: maxwe
"""

import os
import datetime as dt
import pyarrow.feather as feather
import pandas as pd

from common import beginning_of_day, yyyymmdd

# timedelta representing a single day
ONE_DAY = dt.timedelta(1)

def format_stock_data():

    """
    Raw data was stored in the folder data_raw
    Each file is a ticker symbol containing several days worth of data
    
    We want to reformat it in the ../data folder
    Each file is a date containing market data for every symbol that existed on that date
    """    

    print("Reading raw data...")

    # get the list of symbols for which we actually recorded data
    # note that this list will be shorter than the symbol list we downloaded and processed
    symbols = os.listdir('data_raw')
    
    # load all of it into memory
    # market_data is a dictionary of [symbol] that contains dataframes associated with each raw data file
    market_data = {}
    
    # also find the earliest date on which there is data
    date = dt.datetime.today() # dummy value that is very late
    
    # also find the last timestamp on which there is data
    last_timestamp = dt.datetime(1792, 5, 17) # dummy value that is very early
    
    for symbol in symbols:
        
        market_data[symbol] = feather.read_feather('data_raw/'+symbol)
        
        first_date = beginning_of_day(market_data[symbol]['timestamps'][0])
        if first_date < date:
            date = first_date
    
        last_timestamp_symbol = market_data[symbol]['timestamps'].iloc[-1]
        if last_timestamp < last_timestamp_symbol:
            last_timestamp = last_timestamp_symbol

    print("\t...done")

    print("Formatting data...")

    # iterate through days
    while date < last_timestamp:
        print("\t", date)        

        dfs_to_write = []
        
        # for each day, iterate through symbols
        for symbol in symbols:

            # check if there is data on that day
            # if there is, record the elements of the timestamp array 
            #   that correspond to the beginning and end of that day's data
            i_first_timestamp_today = None
            i_last_timestamp_today = None
            for i, timestamp in enumerate(market_data[symbol]['timestamps']):
                
                if i_first_timestamp_today is not None and i_last_timestamp_today is not None:
                    break
                
                if i_first_timestamp_today is None and date < timestamp and timestamp < date + ONE_DAY:
                    i_first_timestamp_today = i
                    
                if i_first_timestamp_today is not None and timestamp < date + ONE_DAY:
                    i_last_timestamp_today = i
                    
            # if there is data...
            if i_first_timestamp_today is not None and i_last_timestamp_today is not None:
                
                # record data
                data_today = list(zip(
                    market_data[symbol]['timestamps'][i_first_timestamp_today:i_last_timestamp_today+1],
                    market_data[symbol]['opens'][i_first_timestamp_today:i_last_timestamp_today+1],
                    market_data[symbol]['highs'][i_first_timestamp_today:i_last_timestamp_today+1],
                    market_data[symbol]['lows'][i_first_timestamp_today:i_last_timestamp_today+1]))
                df_today = pd.DataFrame(data_today, columns=[
                    'timestamps_' + symbol, 
                    'opens_' + symbol, 
                    'highs_' + symbol, 
                    'lows_' + symbol])
                
                dfs_to_write.append(df_today)
            
            # otherwise, there is no data on this day for this symbol

        # if there was data today, there will be dataframes in this list
        if len(dfs_to_write) > 0:
            
            # we now have a bunch of dataframes in a list
            # concatenate them and write a single dataframe
            df_to_write = pd.concat(dfs_to_write, axis=1)
            
            filepath = '../data/' + yyyymmdd(date)
            feather.write_feather(df_to_write, filepath)
            
        # otherwise, there was no data today to write
        
        # move on to the next day
        date += ONE_DAY  

    print("\t...done")



if __name__ == "__main__":

    # this unit test doesn't actually test file conversion
    # instead, it reads converted files and plots their data    

    import matplotlib.pyplot as plt

    data = feather.read_feather('../data/20230406')

    print(data.columns.values)

    print(data['timestamps_MSFT'])
    print(data['opens_MSFT'])
    print(data['highs_MSFT'])
    print(data['lows_MSFT'])

    SYMBOL = 'AAPL'
    plt.plot(data['timestamps_'+SYMBOL], data['opens_'+SYMBOL])
    plt.xticks(rotation=45, ha="right")
    plt.title(SYMBOL)
    plt.show()