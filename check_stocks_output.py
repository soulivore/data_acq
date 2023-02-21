# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 12:44:02 2023

@author: maxwe
"""

import pyarrow.feather as feather
import matplotlib.pyplot as plt

data = feather.read_feather('../data/20230127')

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