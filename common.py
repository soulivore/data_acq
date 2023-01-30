# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 13:55:22 2023

@author: maxwe
"""

import datetime as dt
import re
import atexit
from tda.auth import easy_client


FRAME_PERIOD = 0.51 # frequency in seconds



# returns a datetime with the same date as the input
#   but with hour, min, sec, and us zeroed out
def beginning_of_day(indt):
    
    return dt.datetime(indt.year, indt.month, indt.day)



# format datetime as yyyymmdd ignoring hour, min, sec, and us
def yyyymmdd(indt):
    
    year = str(indt.year)
    month = str(indt.month)
    day = str(indt.day)
    
    if len(month) == 1:
        month = '0'+month
        
    if len(day) == 1:
        day = '0'+day
        
    return year + month + day



# return whether or not a string contains a substring specified by a regex
# case insensitive by default
# https://medium.com/factory-mind/regex-tutorial-a-simple-cheatsheet-by-examples-649dc1c3f285
def string_contains(string, regex, flags=re.IGNORECASE):
    
    regex_comp = re.compile(regex, flags=flags)
    
    if regex_comp.search(string):
        return True
    else:
        return False



# get the client used to query data using the TDA API
def get_client():
    
    # if you are getting new tokens, we'll need to establish a webdriver for the browswer-based login
    def make_webdriver():
        # Import selenium here because it's slow to import
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
    
        driver = webdriver.Chrome(ChromeDriverManager().install())
        #driver = webdriver.Firefox(????)
        atexit.register(lambda: driver.quit())
        return driver
    
    # get api key
    with open('../api_key/api_key.txt', encoding="utf-8") as file:
        api_key = file.read()
    
    # login, getting new tokens if necessary
    client = easy_client(
            api_key=api_key,
            redirect_uri='https://localhost',
            token_path='token.json',
            webdriver_func=make_webdriver)
    
    return client



if __name__ == "__main__":
    
    strings = [
        'Company Unit',
        'Company Units',
        'Company United Healthcare',
        'blargunited'
        ]
    
    for string in strings:
        print(string_contains(string, ' unit($|\s|s$|s\s)'))
        
    strings = [
        'The Company Ltd',
        'Theraputics Company'
        ]
    
    for string in strings:
        print(string_contains(string, '^The '))
        
