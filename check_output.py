# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 12:44:02 2023

@author: maxwe
"""

import pyarrow.feather as feather
import matplotlib.pyplot as plt

data = feather.read_feather('../data/20230127_AAPL')

plt.plot(data['timestamps'], data['opens'])
plt.xticks(rotation=45, ha="right")
plt.show()