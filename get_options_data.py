# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 15:17:46 2023

@author: maxwe
"""

import pandas as pd

from retries import get_option_chain_retry



# get options chain for a particular symbol
# first argument is the easy_client
def get_options_data(client, symbol):
    
    response = get_option_chain_retry(client, symbol)
    
    # if nothing was returned, return nothing
    if response is None:
        return None

    """
    OUTPUT FORMAT NOTES
    not every element of the output will be covered here, as it is extensive
    
    response = dict['symbol', 'status', 'underlying', 'strategy', 'interval', 'isDelayed', 
         'isIndex', 'interestRate', 'underlyingPrice', 'volatility', 
         'daysToExpiration', 'numberOfContracts', 'putExpDateMap', 'callExpDateMap']
    
        response['status'] should equal 'SUCCESS'. Dump the data if it doesn't
        
        response['underlying'] contains info about the underlying stock, including the closing price,
            = dict['symbol', 'description', 'change', 'percentChange', 'close', 
                   'quoteTime', 'tradeTime', 'bid', 'ask', 'last', 'mark', 'markChange', 
                   'markPercentChange', 'bidSize', 'askSize', 'highPrice', 'lowPrice', 
                   'openPrice', 'totalVolume', 'exchangeName', 'fiftyTwoWeekHigh', 
                   'fiftyTwoWeekLow', 'delayed']
            
        response['putExpDateMap'] is a dict of expiration dates in the form 'yyyy-mm-dd:DTE'
            we will use '2023-03-10:18' as an example
        
            response['putExpDateMap']['2023-03-10:18'] is a dict of strike prices
                we will use '150.0' as an example
                
                response['putExpDateMap']['2023-03-10:18']['150.0'] is a list with 1 element
                
                    response['putExpDateMap']['2023-03-10:18']['150.0'][0] is a dict
                        of info about the option
                        = dict['putCall', 'symbol', 'description', 'exchangeName', 'bid', 'ask', 'last', 
                               'mark', 'bidSize', 'askSize', 'bidAskSize', 'lastSize', 
                               'highPrice', 'lowPrice', 'openPrice', 'closePrice', 'totalVolume', 
                               'tradeDate', 'tradeTimeInLong', 'quoteTimeInLong', 'netChange', 
                               'volatility', 'delta', 'gamma', 'theta', 'vega', 'rho', 'openInterest', 
                               'timeValue', 'theoreticalOptionValue', 'theoreticalVolatility', 
                               'optionDeliverablesList', 'strikePrice', 
                               'expirationDate', 'daysToExpiration', 'expirationType', 'lastTradingDay', 
                               'multiplier', 'settlementType', 'deliverableNote', 'isIndexOption', 
                               'percentChange', 'markChange', 'markPercentChange', 'intrinsicValue', 
                               'inTheMoney', 'mini', 'pennyPilot', 'nonStandard']
                        of note are the following:
                            mark = closePrice
                            totalVolume is NOT what we traditionally think of as daily volume
                            openInterest
                            volatility, which appears to be IV expressed as a percent
                            theoreticalVolatility appears to be pretty much the same as volatility
                            delta, gamma, theta, vega
                            multiplier, or the amount you need to multiply the mark by 
                                to get the actual price,
                                i.e. the number of shares per contract
                                should always be 100, but save the data anyway
                            
    For each symbol we will record all available options
        For each option we will record the following:
            DTE (since record date will be recorded)
            strike price
            type (put or call)
            multiplier
            option price (mark)
            volatility
            delta
            gamma
            theta
            vega
    
    print(response.keys())

    print("")
    print(type(response['putExpDateMap']))
    print(response['putExpDateMap'].keys())
    
    print("")
    print(type(response['putExpDateMap']['2023-03-10:18']))
    print(response['putExpDateMap']['2023-03-10:18'].keys())
    
    print("")
    print(type(response['putExpDateMap']['2023-03-10:18']['150.0']), "with", 
          len(response['putExpDateMap']['2023-03-10:18']['150.0']), "elements")

    print("")
    print(type(response['putExpDateMap']['2023-03-10:18']['150.0'][0]))
    print(response['putExpDateMap']['2023-03-10:18']['150.0'][0].keys())
    
    print("")
    print(response['putExpDateMap']['2023-03-10:18']['150.0'][0]['mark'])
    print(response['putExpDateMap']['2023-03-10:18']['150.0'][0]['closePrice'])
    
    """

    if 'status' in response:
        if response['status'] == 'SUCCESS':

            DTE_array = []
            strike_array = []
            type_array = []
            multiplier_array = []
            mark_array = []
            IV_array = []
            delta_array = []
            gamma_array = []
            theta_array = []
            vega_array = []
            
            # iterate over option type, i.e. puts and calls
            for pc_key,pc in zip(['putExpDateMap', 'callExpDateMap'],['p', 'c']):
                
                # iterate over expiration date
                exp_keys = list(response[pc_key].keys())
                
                for exp_key in exp_keys:
                    
                    # iterate over strike prices
                    strike_keys = list(response[pc_key][exp_key].keys())
                    
                    for strike in strike_keys:
                        
                        option = response[pc_key][exp_key][strike][0]
                        
                        # record data
                        DTE_array.append(       exp_key[exp_key.find(':')+1:])
                        strike_array.append(    strike)
                        type_array.append(      pc)
                        multiplier_array.append(float(option['multiplier']))
                        mark_array.append(      float(option['mark']))
                        IV_array.append(        float(option['volatility']))
                        delta_array.append(     float(option['delta']))
                        gamma_array.append(     float(option['gamma']))
                        theta_array.append(     float(option['theta']))
                        vega_array.append(      float(option['vega']))              
                        
            # turn it into a pandas dataframe
            data_out = list(zip(
                DTE_array,
                strike_array,
                type_array,
                multiplier_array,
                mark_array,
                IV_array,
                delta_array,
                gamma_array,
                theta_array,
                vega_array
                ))
        
            df_out = pd.DataFrame(data_out, columns=[
                'DTE',
                'strike',
                'type',
                'multiplier',
                'mark',
                'IV',
                'delta',
                'gamma',
                'theta',
                'vega'
                ])
            
            return df_out
        
        else:
            print("    ", "Warning: options chain response status was", response['status'], ". Returning None.")
            return None
        
    else:
        print("    ", "Warning: options chain response had no data. Returning None.")
        return None
            


from common import get_client

if __name__ == "__main__":

    client = get_client()
    
    df = get_options_data(client, 'AAPL')

    print(df)



