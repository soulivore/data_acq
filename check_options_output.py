# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 17:39:01 2023

@author: maxwe
"""

import pyarrow.feather as feather

data = feather.read_feather('../data/20230220_options')

print(data)