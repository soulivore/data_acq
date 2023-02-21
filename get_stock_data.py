# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 18:45:33 2023

@author: maxwe
"""

from retries import get_price_history_every_minute_retry
import numpy as np
import datetime as dt



# get price and volume data for a particular symbol
# first argument is the easy_client
def get_stock_data(client, symbol):
    
    response = get_price_history_every_minute_retry(
        client, 
        symbol, 
        need_extended_hours_data=False)

    """
    OUTPUT FORMAT NOTES
    
    dict['candles', 'symbol', 'empty']
        symbol = ticker symbol
        empty = appears to be equal to False. Maybe it's True if there's a problem
        candles = list of dicts, each corresponsing to a different datetime
            dict['open', 'high', 'low', 'close', 'volume', 'datetime']
            
            
    each number is of type float
    data is recorded every minute
    each minute contains the following data sizes:
        open-close: 24 bits each
        volume: 28 bits
        datetime: 32 bits
        total per minute: 156 bits/min
    
    (156 bits/min)*(60 min/hr)*(6.5 hrs/day) = 7.6 kB/stock/day
    *(6000 stocks) = 45 MB/day
    
    You can get minute-by-minute data for the past 48 days
    (45 MB/day)*(48 days) = 2.16 GB
    My computer tends to have 6 GB of RAM free, so we could load in all 2.16 GB
        and then split it out into files by the day (or keep it as one big file)
    (It's actually a little less because not all 48 days are trading days.)
    
    There are 252 trading days in a year
    This will consume (45 MB/day)*(252 days/yr) = 11.34 GB/yr
    Worth
    
    We can cut it down a little by recognizing that the "close" on one candle 
        is the same (or should be the same) as the "open" on the next candle  
    In each set of recorded data, there will be one additional row 
        that indicates the closing value of the previous row 
    """

    if response is None:
        return None, None, None, None

    N = len(response['candles']) + 1
    
    # if data was returned
    if N > 1:
        
        timestamps = np.empty(N, dtype=dt.datetime)
        opens =      np.zeros(N)
        highs =      np.zeros(N)
        lows =       np.zeros(N)
    
        for i,e in enumerate(response['candles']):
            
            timestamps[i] = dt.datetime.fromtimestamp(e['datetime']//1000)
            opens[i] =      e['open']
            highs[i] =      e['high']
            lows[i] =       e['low']
        
        timestamps[N-1] = timestamps[N-2] + dt.timedelta(minutes=1)
        opens[N-1] =      e['close']
        highs[N-1] =      np.nan
        lows[N-1] =       np.nan
        
        return timestamps, opens, highs, lows
    
    else:
        return None, None, None, None
    


if __name__ == "__main__":
    
    from common import get_client
    import matplotlib.pyplot as plt
    
    client = get_client()
    
    timestamps, opens, highs, lows = get_stock_data(client, 'AAPL')
    
    plt.plot(timestamps, opens)
    plt.xticks(rotation=45, ha="right")
    plt.show()