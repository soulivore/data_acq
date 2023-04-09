# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 13:33:38 2023

@author: maxwe
"""

from common import get_client
from get_symbols import get_symbols, write_symbols, read_symbols
from write_stock_data_raw import write_stock_data_raw
from format_stock_data import format_stock_data

# get API client
client = get_client()

# get and store list of symbols
symbols = get_symbols(client)
write_symbols(symbols)
symbols = read_symbols()

# get and store raw market data for those symbols
write_stock_data_raw(client, symbols)

# format the raw data into files organized by date
format_stock_data()