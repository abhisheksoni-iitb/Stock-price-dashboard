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


st.title('Stock Price Dashboard')

st.markdown("""
Select the Stock and explore an interactive graph
""")
stock_exchange = st.selectbox('Select the Stock Exchange', [None,'National Stock Exchange', 'Bombay Stock Exchange'])

stock = st.selectbox('Select the Stock', [None,'RELIANCE', 'HDFCBANK', 'ADANIPORTS', 'ITC', 'SBI', 'IOC', 'RBLBANK'])


def get_price_history(ticker, sdate, edate):
    data = []
    data = yf.download(ticker, start=sdate, end=edate,rounding=True)
    return (data)


def plots(df):
    cndlstck = go.Candlestick(
        x = df.index, 
        open = df['Open'], 
        high = df['High'], 
        low = df['Low'], 
        close = df['Close']
        )

    df['EMA_9'] = df['Close'].ewm(5).mean().shift()
    df['SMA_50'] = df['Close'].rolling(50).mean().shift()
    df['SMA_100'] = df['Close'].rolling(100).mean().shift()



    fig = go.Figure(data = [cndlstck])
    # fig.add_volume(go.Scatter(x=list(df.index), y=list(df['High']),name='High'))
    fig.add_trace(go.Scatter(x=df.index, y=df.EMA_9, name='EMA 9', opacity=0.2))
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA_50, name='SMA 50', opacity=0.2))
    fig.add_trace(go.Scatter(x=df.index, y=df.SMA_100, name='SMA 100', opacity=0.2))
    fig.add_trace(go.Scatter(x=df.index, y=df.Close, name='Close', line_color='dimgray', opacity=0.2))

    fig.update_layout(
        title="Time series with range slider and selectors",
        yaxis_title = 'Stock Price',
        xaxis_title = 'Date'

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

        fig = plots(df)
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

        fig = plots(df)
        st.plotly_chart(fig)
        
