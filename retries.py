# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 21:03:35 2023

@author: maxwe
"""

"""
This is a wrapper for the TDA API calls
These functions are called in lieu of the actual API calls
They call the API call in a try block and retry multiple times
at a given periodicity until success or max retries
"""

import httpx
import time
from tda.client import Client as tcc



MAX_RETRIES = 50
RETRY_PERIOD = 5 # s



def get_price_history_every_minute_retry(client, symbol, need_extended_hours_data=None):
    
    retries = 0
    while retries <= MAX_RETRIES:
    
        try:
        
            response_raw = client.get_price_history_every_minute(
                symbol, 
                need_extended_hours_data=need_extended_hours_data)
            assert response_raw.status_code == httpx.codes.OK
            
            response = response_raw.json()
            
            return response
            
        except AssertionError:
            
            print("Assertion failed in get_price_history_ever_minute(). Retrying...")

        except:
            
            print("Exception caught in get_price_history_ever_minute(). Retrying...")
            
        retries += 1
        time.sleep(RETRY_PERIOD)
        
    # max retries exceeded
    print("Maximum retries exceeded. Aborting.")
    return None
        
            
        
def get_option_chain_retry(client, symbol):
    
    retries = 0
    
    while retries <= MAX_RETRIES:
    
        try:
            
            response_raw = client.get_option_chain(
                symbol,
                contract_type=tcc.Options.ContractType.ALL,
                include_quotes=True)
            assert response_raw.status_code == httpx.codes.OK
            
            response = response_raw.json()
            
            return response
        
        except AssertionError:
            
            print("Assertion failed in get_option_chain(). Retrying...")

        except:
            
            print("Exception caught in get_option_chain(). Retrying...")
            
        retries += 1
        time.sleep(RETRY_PERIOD)
        
    # max retries exceeded
    print("Maximum retries exceeded. Aborting.")
    return None        