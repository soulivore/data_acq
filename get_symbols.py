# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 12:20:55 2023

@author: maxwe
"""

import httpx
from tda.client import Client as tcc
import re
import time

from common import string_contains, FRAME_PERIOD



alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'



# remove "The" or "the" from the beginning of a string
def remove_desc_prefix(desc):
    
    if string_contains(desc, '^The '):
        return desc[4:] 
    else:
        return desc   



def get_symbols(client):
    
    symbols = []
    
    print("Downloading symbol lists...", end='')
    
    # see below for why we're getting symbol info letter by letter
    for letter in alphabet:
        
        frame_start = time.time() # for frame timing
        
        print(letter, end='')
        
        search_phrase = letter+'.*'
        
        # query basic info in a bunch of symbols defined by the regex below
        # the status code assertion fails if you try to use '.+' or '.*', 
        #   but it works if you go through the alphabet by first letter of the symbol    
        response_raw = client.search_instruments(search_phrase, tcc.Instrument.Projection.SYMBOL_REGEX)
        # also note that you can use the following to get fundamentals about an exactly-specified symbol:
        #   response_raw = client.search_instruments('AAPL', tcc.Instrument.Projection.FUNDAMENTAL)
        
        assert response_raw.status_code == httpx.codes.OK
        response = response_raw.json()
        
        """
        OUTPUT FORMAT NOTES
        
        output for client.search_instruments('some regex expression for ticker symbol', tcc.Instrument.Projection.SYMBOL_REGEX)
        
        dict[symbol]
            dict['cusip', 'symbol', 'description', 'exchange', 'assetType']
                cusip    
                symbol    
                description = name of company and type of stock
                exchange = NYSE, NASDAQ, etc (filter out everything except NYSE and NASDAQ)
                assetType = EQUITY, ETF, etc (filter out everything except EQUITY)
    
        output for client.search_instruments('exact symbol', tcc.Instrument.Projection.FUNDAMENTAL)
        
        dict[symbol]
            dict['fundamental', 'cusip', 'symbol', 'description', 'exchange', 'assetType']
                (everything except 'fundamental' is the same as above)
                fundamental = dict['symbol', 'high52', 'low52', 'dividendAmount', 'dividendYield', 'dividendDate', 'peRatio', 
                                   'pegRatio', 'pbRatio', 'prRatio', 'pcfRatio', 'grossMarginTTM', 'grossMarginMRQ', 
                                   'netProfitMarginTTM', 'netProfitMarginMRQ', 'operatingMarginTTM', 'operatingMarginMRQ', 
                                   'returnOnEquity', 'returnOnAssets', 'returnOnInvestment', 'quickRatio', 'currentRatio', 
                                   'interestCoverage', 'totalDebtToCapital', 'ltDebtToEquity', 'totalDebtToEquity', 'epsTTM', 
                                   'epsChangePercentTTM', 'epsChangeYear', 'epsChange', 'revChangeYear', 'revChangeTTM', 
                                   'revChangeIn', 'sharesOutstanding', 'marketCapFloat', 'marketCap', 'bookValuePerShare', 
                                   'shortIntToFloat', 'shortIntDayToCover', 'divGrowthRate3Year', 'dividendPayAmount', 
                                   'dividendPayDate', 'beta', 'vol1DayAvg', 'vol10DayAvg', 'vol3MonthAvg']
        """

        for symbol in response.keys():
            
            if 'exchange' in response[symbol] and 'description' in response[symbol]:         
                
                exchange = response[symbol]['exchange']
                if (exchange == 'NYSE' or exchange == 'NASDAQ') and response[symbol]['assetType'] == 'EQUITY':
                    
                    symbols.append((symbol, remove_desc_prefix(response[symbol]['description'])))
        
        # throttle to frame period
        time_spent = time.time() - frame_start
        if time_spent < FRAME_PERIOD:
            time.sleep(FRAME_PERIOD - time_spent)
    
    symbols.sort()    
    
    # this list contains a lot of symbols that are duplicated but with different suffixes
    # use the symbols and their descriptions to try and filter out the duplicates
    # https://www.investopedia.com/terms/s/stocksymbol.asp        
    
    print("\nProcessing list...")
    
    # For each symbol,...
    i = 0
    while i < len(symbols):
        symbol = re.split('[^a-zA-Z]', symbols[i][0])[0] # specifically look at the symbol preceding any punctuation or numbers
        desc = symbols[i][1]
        
        # ... compare it to the next symbol and check the following:
        j = i + 1
        while j < len(symbols):
            next_symbol = symbols[j][0]
            next_desc = symbols[j][1]
            
            # If this symbol is equal to the last symbol plus extra characters after...
            if next_symbol.find(symbol) == 0:
                
                # ...it might be the same company but with a modified symbol.
                # Check if their descriptions start with the same word
                if desc.split(' ')[0] == next_desc.split(' ')[0]:
            
                    # remove this entry, then check the next one
                    symbols.pop(j)
                    continue
                
                # symbol j had the same string of characters at the beginning as symbol i, 
                #   but was not the same company.
                # but the next symbol match beginning characters AND be the same company.
                # check the next symbol
                else:
                    j += 1
                    continue
            
            # symbol j was unrelated to symbol i
            # move on to the next symbol i
            else:
                break

        
        # if the current symbol has an alert associated with it, delete it
        if string_contains(desc, ' alert'):
            
            symbols.pop(i)
        
        # if the current symbol is a warrant, delete it
        elif string_contains(desc, ' warrant'):
            
            symbols.pop(i)
            
        # if the current symbol is a unit, whatever that is, delete it
        elif string_contains(desc, ' unit($|\s|s$|s\s)'):
        
            symbols.pop(i)
            
        # if the current symbol is a note, delete it
        elif string_contains(desc, ' notes '):
            
            symbols.pop(i)
            
        # if the current symbol is some sort of fixed-return instrument, delete it
        elif string_contains(desc, '%'):
            
            symbols.pop(i)
            
        else:
            
            i += 1
            
    print("\t...done")
    
    return symbols



def write_symbols(symbols):
    
    print("Writing list...")
    
    with open('symbols.txt', 'w', encoding="utf-8") as file:
        for e in symbols:
            symbol = e[0] + "\n"
            file.write(symbol)
            
    print("\t...done")
    


def read_symbols():
    
    print("Reading symbols...")
    
    symbols = []
    
    with open('symbols.txt', encoding="utf-8") as file:
        for line in file:
            symbols.append(line.strip())
            
    print("\t...done")
    
    return symbols

    
    
if __name__ == "__main__":
    
    from common import get_client
    
    client = get_client()
    
    symbols = get_symbols(client)
    
    write_symbols(symbols)
    

    
    