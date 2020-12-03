import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import quandl
import plotly.graph_objects as go
from plotly import tools
import plotly.offline as py
import plotly.express as px
import yfinance as yf
import datetime
from datetime import date
from plotly.subplots import make_subplots


st.title('Stock Price Dashboard')

st.markdown("""
Select the Stock and explore an interactive graph
""")
stock_exchange = st.selectbox('Select the Stock Exchange', [None,'National Stock Exchange', 'Bombay Stock Exchange'])

stock = st.selectbox('Select the Stock', [None,'RELIANCE', 'HDFCBANK', 'ADANIPORTS', 'ITC', 'SBI', 'IOC', 'RBLBANK'])


def get_price_history(ticker, sdate, edate):
    data = []
    data = yf.download(ticker, start=sdate, end=edate,rounding=True)
    data.drop(['Adj Close'],1,inplace=True)
    return (data)


def plots(df , plot_option,stock_selected):
    fig = go.Figure(data = [])
    if plot_option == 'Candle-Stick':
        cndlstck = go.Candlestick(
            x = df.index, 
            open = df['Open'], 
            high = df['High'], 
            low = df['Low'], 
            close = df['Close']
            )
        fig = go.Figure(data = [cndlstck])

    elif plot_option == 'Moving Average':
        df['EMA_9'] = df['Close'].ewm(5).mean().shift()
        df['SMA_50'] = df['Close'].rolling(50).mean().shift()
        df['SMA_100'] = df['Close'].rolling(100).mean().shift()
        fig = go.Figure(data = [])
        fig.add_trace(go.Scatter(x=df.index, y=df.EMA_9, name='Exponential Moving Avg(9) ', opacity=0.8))
        fig.add_trace(go.Scatter(x=df.index, y=df.SMA_50, name='Moving Avg50', opacity=0.8))
        fig.add_trace(go.Scatter(x=df.index, y=df.SMA_100, name='Moving Avg100', opacity=0.8))
        fig.add_trace(go.Scatter(x=df.index, y=df.Close, name='Close', line_color='dimgray', opacity=0.8))

    elif plot_option == 'Relative Strength Index (RSI)':
        
        def RSI(df, n=14):
            close = df['Close']
            delta = close.diff()
            delta = delta[1:]
            pricesUp = delta.copy()
            pricesDown = delta.copy()
            pricesUp[pricesUp < 0] = 0
            pricesDown[pricesDown > 0] = 0
            rollUp = pricesUp.rolling(n).mean()
            rollDown = pricesDown.abs().rolling(n).mean()
            rs = rollUp / rollDown
            rsi = 100.0 - (100.0 / (1.0 + rs))
            return rsi

        num_days = 365
        df['Date']= df.index
        df['RSI'] = RSI(df).fillna(0)
        fig = go.Figure(go.Scatter(x=df.Date.tail(num_days), y=df.RSI.tail(num_days)))
        fig.update_layout(
            title=str(stock_selected)+" Relative Strength Index (RSI) plot",
            yaxis_title = 'RSI (%)',

        )
        # fig.show()

    elif plot_option == 'Moving Average Convergence Divergence (MACD)':
        df['Date']= df.index
        EMA_12 = pd.Series(df['Close'].ewm(span=12, min_periods=12).mean())
        EMA_26 = pd.Series(df['Close'].ewm(span=26, min_periods=26).mean())
        MACD = pd.Series(EMA_12 - EMA_26)
        MACD_signal = pd.Series(MACD.ewm(span=9, min_periods=9).mean())
        fig = go.Figure(data = [])
        fig = make_subplots(rows=2, cols=1)
        fig.add_trace(go.Scatter(x=df.Date, y=df.Close, name='Close'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.Date, y=EMA_12, name='EMA 12'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.Date, y=EMA_26, name='EMA 26'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.Date, y=MACD, name='MACD'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.Date, y=MACD_signal, name='Signal line'), row=2, col=1)
        # fig.show()
        fig.update_layout(
            title=str(stock_selected)+" MACD plot",
            yaxis_title = 'MACD ',

        )
  
    fig.update_layout(hovermode="x", xaxis = {'showspikes': True}, yaxis = {'showspikes': True})
    if plot_option not in  ['Relative Strength Index (RSI)','Moving Average Convergence Divergence (MACD)']:
        
        fig.update_layout(
            title=str(stock_selected)+" Stock price at various time",
            yaxis_title = 'Stock Price',

        )
        
    

    fig.layout.xaxis.type = 'category'
    # fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='black', opacity=0.05))
    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,label="1m",step="month",stepmode="backward"),
                    dict(count=6,label="6m",step="month",stepmode="backward"),
                    dict(count=1,label="YTD",step="year",stepmode="todate"),
                    dict(count=1,label="1y",step="year",stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    fig.update_layout(width=800,height=600)
    return fig

# @st.cache
if stock_exchange is not None:
    if (stock is not None) and (stock_exchange == 'Bombay Stock Exchange'):

        stock_map = {
                    'RELIANCE':"RELIANCE.BO", 
                    'HDFCBANK':"HDFCBANK.BO", 
                    'ADANIPORTS':"ADANIPORTS.BO", 
                    'ITC':"ITC.BO", 
                    'SBI':"SBIN.BO", 
                    'IOC':"IOC.BO", 
                    'RBLBANK':"RBLBANK.BO"
                }

        
        df = get_price_history(stock_map[stock], date(2016,1,1), datetime.datetime.now().date())
        st.dataframe(df[::-1],width=1000)


        plot_option = st.selectbox('Select the Visual', ['Candle-Stick', 'Moving Average',
                                             'Relative Strength Index (RSI)', 'Moving Average Convergence Divergence (MACD)'])
        fig = plots(df,plot_option,stock)
        st.plotly_chart(fig)

    elif (stock is not None) and (stock_exchange ==  'National Stock Exchange'):

        

        stock_map = {
                    'RELIANCE':"RELIANCE.NS", 
                    'HDFCBANK':"HDFCBANK.NS", 
                    'ADANIPORTS':"ADANIPORTS.NS", 
                    'ITC':"ITC.NS", 
                    'SBI':"SBIN.NS", 
                    'IOC':"IOC.NS", 
                    'RBLBANK':"RBLBANK.NS"
                }
    
        df = get_price_history(stock_map[stock], date(2016,1,1), datetime.datetime.now().date())
        st.dataframe(df[::-1],width=1000)

        plot_option = st.selectbox('Select the Visual', ['Candle-Stick', 'Moving Average',
                                             'Relative Strength Index (RSI)', 'Moving Average Convergence Divergence (MACD)'])

        fig = plots(df,plot_option,stock)
        st.plotly_chart(fig)
        
