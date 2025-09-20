import numpy as np
import math

from dal.service import DalService
from model import train_pricing_model, predict_price 

# function that return a float
# rfq is an object with 2 attributes qty and stock name (universe S&P 500)
def answer_rfq(rfq):
    days_long = 26
    days_histo = 26
    
    # loading the historical price
    price_stock_hist = DalService.get_prices(rfq.get_sym()).tail(days_histo)
   
    hist_volume = DalService.get_volumes(rfq.get_sym()).tail(days_histo)
    med_volume = np.median(hist_volume)

    macD = DalService.get_macd(price_stock_hist).iloc[-1].values[0]
    print(macD)
    macDsignal = DalService.get_macd_signal_line(price_stock_hist).iloc[-1].values[0]
    macD_previous = DalService.get_macd(price_stock_hist).iloc[-2].values[0]
    macDsignal_previous = DalService.get_macd_signal_line(price_stock_hist).iloc[-2].values[0]

    earnings_all = DalService.get_earnings_all(rfq.get_sym())
    print(earnings_all)
    earning_prev = DalService.get_earnings_prev(rfq.get_sym())['actual']
    earning_next = DalService.get_earnings_next(rfq.get_sym())['actual']
    diff_earnings = 0
    if earning_prev is None or earning_next is None:
        diff_earnings = 0
    else: 
        diff_earnings = earning_next - earning_prev
    print(diff_earnings)
    
    diff_macD = macD - macDsignal
    diff_macD_previous = macD_previous - macDsignal_previous

    previous_close = price_stock_hist.iloc[-1].values[0]
    #discretionnary factor applied to the price depending on various factors
    price_factor=0
    volatilities = DalService.get_volatilities(price_stock_hist, days_long)
    print(volatilities)

    param = {'diff_earnings' : diff_earnings,
            'macD_diff' : diff_macD , 
            'macD_signal_diff' : diff_macD_previous, 
            'volatilities' : volatilities}

    # qty is neg we return the opposite price
    if rfq.get_qty() >0:
        sign = 1
    else:
        sign = -1
    if macDsignal_previous < macD_previous and macD > macDsignal:
        price_factor *= (1 + sign*0.01)
        return previous_close * price_factor
    elif macDsignal_previous < macD_previous and macD < macDsignal:
        return None
    elif macDsignal_previous > macD_previous and macD < macDsignal:
        price_factor *= (1 + sign*0.01)
        return previous_close * price_factor
    else:
        return None
    