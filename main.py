from xml.etree.ElementInclude import include

import pandas as pd
import pandas_ta as ta
import requests
import ccxt
import streamlit as st

ticker = "ETH/USDT"
timeframe = "30m"
periods = 500
begin = False
rsiBuy = 14
rsiSell = 14
bollingerBuy = 1
bollingerSell = 1
macdFastBuy = 12
macdFastSell = 12
macdSlowBuy = 26
macdSlowSell = 26
macdSmoothBuy = 9
macdSmoothSell = 9
emaBuy = 10
emaSell = 10
df = pd.DataFrame()
dfBuy = pd.DataFrame()
dfSell = pd.DataFrame()

st.title('Backtesting bot')
ticker = st.text_input('What Binance Coin are you interested in backtesting?',placeholder="ETH/USDT")
timeframe = st.selectbox('On what timeframe shold the timeframe be tested on?',('5m', '15m', '30m', '1h', '1d', '1w'))
periods = st.number_input('How many periods are you looking to backtest?', 0, 600)
st.title("Setup indicators")
buy, sell = st.columns(2)
with buy:
    indicatorsBuy = st.multiselect('What indicators do you want to use for the buy condition',['Rsi', 'Bollinger', 'Macd', 'Ema'])
    if 'Rsi' in indicatorsBuy:
        rsiBuy = st.number_input('What period rsi for the buy condition: ', 14)
    if 'Bollinger' in indicatorsBuy:
        bollingerBuy = st.number_input('How many standard diviations for the bollinger buy condition: ', 1)
    if 'Macd' in indicatorsBuy:
        macdFastBuy = st.number_input('Macd Fast Signal: ', 12)
        macdSlowBuy = st.number_input('Macd Slow Signal: ', 26)
        macdSmoothBuy = st.number_input('Macd signal smoothing: ', 9)
    if 'Ema' in indicatorsBuy:
        emaBuy = st.number_input('What ema period for the buy condition: ', 2, periods)

with sell:
    indicatorsSell = st.multiselect('What indicators do you want to use for the sell condition',['Rsi', 'Bollinger', 'Macd', 'Ema'])
    if 'Rsi' in indicatorsSell:
        rsiSell = st.number_input('What period rsi for the sell condition: ', 14)
    if 'Bollinger' in indicatorsSell:
        bollingerSell = st.number_input('How many standard diviations for the bollinger sell condition: ', 1)
    if 'Macd' in indicatorsSell:
        macdFastSell = st.number_input('Macd Fast Signal: ', 12)
        macdSlowSell = st.number_input('Macd Slow Signal: ', 26)
        macdSmoothSell = st.number_input('Macd signal smoothing: ', 9)
    if 'Ema' in indicatorsSell:
        emaSell = st.number_input('What ema period for the sell condition: ', 2, periods)


def load():
    global df,rsiBuy,rsiSell,emaBuy,emaSell,macdFastBuy,macdFastSell,macdSlowBuy,macdSlowSell,macdSmoothBuy,macdSmoothSell,bollingerBuy,bollingerSell
    df = pd.DataFrame(ccxt.binance().fetch_ohlcv(ticker, timeframe=timeframe, limit = periods), columns=["time", "open", "high", "low", "close", "volume"])
    dfBuy = pd.concat([df, df.ta.rsi(rsiBuy), df.ta.ema(emaBuy), df.ta.macd(macdFastBuy,macdSlowBuy,macdSmoothBuy), df.ta.bbands(bollingerBuy)],axis = 1)
    dfSell = pd.concat([df, df.ta.rsi(rsiSell), df.ta.ema(emaSell), df.ta.macd(macdFastSell, macdSlowSell, macdSmoothSell),df.ta.bbands(bollingerSell)],axis = 1)
    return dfBuy, dfSell

show = st.button("Show the data")
if(show):
    dfBuy,dfSell = load()
    st.write("Buying data dataframe:")
    st.write(dfBuy)
    st.write("Selling data dataframe:")
    st.write(dfSell)

st.title("Simulate")
buy2, sell2 = st.columns(2)
with buy2:
    if 'Rsi' in indicatorsBuy:
        rsiBuyUnder = st.number_input('Buy when rsi is lower than: ')
    if 'Ema' in indicatorsBuy:
        emaBuyUnder = st.number_input('Buy when price under ema plus: ')

with sell2:
    if 'Rsi' in indicatorsSell:
        rsiSellOver = st.number_input('Sell when rsi is higher than: ')
    if 'Ema' in indicatorsSell:
        emaSellOver = st.number_input('Sell when price oper ema plus: ')


calculate = st.button("Do the testing")
if calculate:
    balance = 10000
    buyPrice = None
    sellPrice = None
    inPosition = False
    dfBuy,dfSell = load()
    for i in range(len(dfBuy)):
        if(inPosition):
            if dfSell[f'RSI_{rsiSell}'][i] > rsiSellOver:
                sellPrice = dfBuy['close'][i]
                profit = sellPrice-buyPrice
                balance += balance * profit/buyPrice
                st.write(f'Bought at {buyPrice}, sold al {sellPrice}, profit: {round(profit/buyPrice*100,2)}% {balance}$')
                inPosition = False
        else:
            if dfBuy[f'RSI_{rsiBuy}'][i] < rsiBuyUnder:
                buyPrice = dfBuy['close'][i]
                inPosition = True