import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
# import yfinance as yf
import quandl
import plotly.graph_objects as go
from plotly import tools
import plotly.offline as py
import plotly.express as px



st.title('Stock Price Dashboard')

st.markdown("""
This app retrieves the list of the **S&P 500** (from Wikipedia) and its corresponding **stock closing price** (year-to-date)!
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
* **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
""")

stock = st.selectbox('Select the Stock', [None,'RELIANCE', 'HDFCBANK', 'ADANIPORTS', 'ITC', 'SBI', 'IOC', 'RBLBANK'])

stock_map = {
    'RELIANCE':"BSE/BOM500325", 
    'HDFCBANK':"BSE/BOM500180", 
    'ADANIPORTS':"BSE/BOM532921", 
    'ITC':"BSE/BOM500875", 
    'SBI':"BSE/BOM500112", 
    'IOC':"BSE/BOM540065", 
    'RBLBANK':"BSE/BOM540065"
}
# Web scraping of S&P 500 data
#
if stock is not None:
    # @st.cache
    def get_data(stock_code):
        df = quandl.get(stock_code, authtoken="_j-x2o8Gk93gkkqyE6tG")

        #cleaning the data
        features_to_drop = ['No. of Shares', 'No. of Trades','Spread H-L', 'Spread C-O']
        df.drop(features_to_drop,1,inplace=True)
        df.rename(columns = {'WAP': 'Volume' },
                inplace = True)
        # df['Volume'] = df['WAP']
        # df.drop(['WAP'],1, inplace = True)
        df.dropna(inplace=True)
        return df

    df = get_data(stock_map[stock])

    def plots(df):
        cndlstck = go.Candlestick(
            x = df.index, 
            open = df['Open'], 
            high = df['High'], 
            low = df['Low'], 
            close = df['Close'], showlegend = True
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
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='black', opacity=0.05))
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
        return fig
        # fig.update_layout(rangeslider=dict(visible=True))
        #   fig.show()

    fig = plots(df)
    st.plotly_chart(fig)
