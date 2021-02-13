# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 13:59:04 2021

@author: youss
"""

import pandas as pd
from Stocks import Stock


def normalize (x):
    x[x>0.001] = x[x>0.001] / x[x>0.001].sum()
    x[x<0.001] = x[x<0.001] / - x[x<0.001].sum()
    return x


def build_view(signal_func, stock_arr, n_buckets = None):
    stock_arr = [Stock(s) if isinstance(s, str) else s for s in stock_arr]
    output_dict = {}
    for s in stock_arr:
        output_dict[s.ticker] = signal_func(s)
    signal_df = pd.DataFrame(output_dict).dropna()
    if n_buckets is None:
        view_df = signal_df.rank(pct = True, axis = 1).apply(lambda x: x - x.mean(), axis = 1).apply(lambda x: normalize(x), axis = 1)
    else:
        view_df = signal_df.apply(lambda x: pd.qcut(x, n_buckets, labels = False), axis = 1)
        big_bucket_idx = view_df == (n_buckets - 1)
        small_bucket_idx = view_df == 0
        view_df.loc[:,:] = 0
        view_df[big_bucket_idx] = 1
        view_df[small_bucket_idx] = -1
        view_df = view_df.apply(lambda x: normalize(x), axis = 1)

    return view_df
  
'''      
signal_func = lambda s: (s['PriceClose'] / s['TotalRevenue']).rolling(window=21).apply(lambda x: (x[-1] - x.mean())/(x.std()))
  
df = build_view(signal_func, stock_arr = ['FB', 'AAPL', 'MSFT', 'NFLX', 'GOOGL'], n_buckets = 3)
'''      
        
def build_returns (stock_arr):
    stock_arr = [Stock(s) if isinstance(s, str) else s for s in stock_arr]
    output_dict = {}
    for s in stock_arr:
        output_dict[s.ticker] = s['PriceClose']
    price_df = pd.DataFrame(output_dict).dropna()
    returns_df = price_df.pct_change(1)
    return returns_df

def build_weights (stock_arr):
    stock_arr = [Stock(s) if isinstance(s, str) else s for s in stock_arr]
    output_dict = {}
    for s in stock_arr:
        output_dict[s.ticker] = s['PriceClose'] * s['ShareIssued']
    marketcap_df = pd.DataFrame(output_dict).dropna()   
    weights_df = marketcap_df.apply(lambda x: normalize(x), axis = 1)
    return weights_df

def black_litterman_weights(stock_universe, view_arr, tau=1.0, lam=0.5 ):
    stock_universe = [Stock(s) if isinstance(s, str) else s for s in stock_universe]   
    weights_df = build_weights(stock_universe).iloc[-1,:]
    returns_df = build_returns(stock_universe)
    Sigma = returns_df.cov() * 252  
    Pi = 2 * lam * Sigma.dot(weights_df)
        
