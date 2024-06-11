import sqlite3
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta


connection = sqlite3.connect('data/bio/candles.db')

def get_candles(ticker: str, day: datetime):
    df_2m = pd.read_sql(f'SELECT * FROM {ticker}', connection)
    df_2m['Datetime'] = pd.to_datetime(df_2m['Datetime'])
    df_2m = df_2m[
        (df_2m['Datetime'] > day - timedelta(days=2)) &
        (df_2m['Datetime'] < day + timedelta(days=3))
    ]

    df_15m: pd.DataFrame = yf.download(ticker, start=day-timedelta(days=14), end=day+timedelta(days=4), interval='15m', prepost=True).reset_index()
    df_1d: pd.DataFrame = yf.download(ticker, start=day-timedelta(days=5*365), end=day+timedelta(days=4), interval='1d', prepost=True).reset_index()

    return df_2m, df_15m, df_1d


while True:
    ticker, day = input('ticker YYYY-MM-DD: ').split()
    df_2m, df_15m, df_1d = get_candles(ticker, datetime.fromisoformat(day + 'T00:00:00Z-04:00'))

    fig = make_subplots(
        rows=2, cols=2,
        specs=[
            [{}, {}],
            [{'colspan': 2}, None]
        ],
        subplot_titles=('15M', '1D', '2M'),
        vertical_spacing=0.05
    )

    fig.add_trace(
        go.Candlestick(x=df_15m['Datetime'], open=df_15m['Open'], high=df_15m['High'], low=df_15m['Low'], close=df_15m['Close']),
        row=1, col=1
    )
    fig.add_trace(
        go.Candlestick(x=df_1d['Date'], open=df_1d['Open'], high=df_1d['High'], low=df_1d['Low'], close=df_1d['Close']),
        row=1, col=2
    )
    fig.add_trace(
        go.Candlestick(x=df_2m['Datetime'], open=df_2m['Open'], high=df_2m['High'], low=df_2m['Low'], close=df_2m['Close']),
        row=2, col=1
    )
    for i in range(5):
        dt0 = df_2m.iloc[0, 0] + timedelta(days=i)
        if dt0 > df_2m.iloc[-1, 0]:  # eksdee
            break
        fig.add_vrect(
            x0=dt0.replace(hour=4), x1=dt0.replace(hour=9, minute=30), fillcolor='orange', opacity=0.1,
            row=2, col=1
        )
        fig.add_vrect(
            x0=dt0.replace(hour=16), x1=dt0.replace(hour=20), fillcolor='blue', opacity=0.1,
            row=2, col=1
        )

    fig.update_xaxes(rangeslider={'visible': False})
    fig.update_layout(showlegend=False, height=2000)

    fig.write_html(f'data/bio/charts/{ticker}_{day}.html')
    