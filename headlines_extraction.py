import psycopg2
import time
import pytz
import threading
import os
import datetime
import pandas as pd
from finvizfinance.quote import finvizfinance
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_connection():
    try:
        connection = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            options='-c statement_timeout=1020000'
        )

    except psycopg2.OperationalError as e:
        print(f'Error: {e}')
        return None

    else:
        print('Connected Established!')
        return connection
conn = get_connection()
cursor = conn.cursor()
query = '''
SELECT Ticker FROM Stocks
'''

cursor.execute(query)
tickers = cursor.fetchall()
tickers = [ticker[0] for ticker in tickers]
news_dfs = {}

def get_news(ticker):
    print(f'Fetching headlines for {ticker}...')
    stock = finvizfinance(ticker)
    news_df = stock.ticker_news()
    return news_df 

def fetch_headlines(ticker):
    try:
        news_dfs[ticker] = get_news(ticker)
    except Exception as e:
        print(f"Error fetching headlines for {ticker}: {e}")
        fetch_headlines(ticker)

with ThreadPoolExecutor(max_workers=2) as executor:
    for i, ticker in enumerate(tickers):
        executor.submit(fetch_headlines, ticker)

current_time = datetime.datetime.now(pytz.timezone('US/Eastern'))
et_now = current_time.replace(second=0, microsecond=0).replace(tzinfo=None)
def convert_to_ET(dt):
    eastern = pytz.timezone('US/Eastern')
    return dt.astimezone(eastern)

def extract_headlines_within_one_day(df, current_time):
    one_day_ago = current_time - pd.Timedelta(days=1)
    return df[df['Date'] >= one_day_ago]

def extract_headlines_within_one_week(df, current_time):
    one_week_ago = current_time - pd.Timedelta(weeks=1)
    return df[df['Date'] >= one_week_ago]

def extract_headlines_within_one_month(df, current_time):
    one_month_ago = current_time - pd.Timedelta(days=30)
    return df[df['Date'] >= one_month_ago]

def extract_headlines_within_timeframes(dictionary_of_dataframes):
    current_time_ET = convert_to_ET(datetime.datetime.now())
    current_time_ET = current_time_ET.replace(second=0, microsecond=0).replace(tzinfo=None)

    headlines_within_timeframes = {}

    for stock, df in dictionary_of_dataframes.items():
        daily_headlines = extract_headlines_within_one_day(df, current_time_ET)
        weekly_headlines = extract_headlines_within_one_week(df, current_time_ET)
        monthly_headlines = extract_headlines_within_one_month(df, current_time_ET)
        
        headlines_within_timeframes[stock] = {
            'Daily': daily_headlines,
            'Weekly': weekly_headlines,
            'Monthly': monthly_headlines
        }
    
    return headlines_within_timeframes

df = extract_headlines_within_timeframes(news_dfs)

dfs = []

for ticker, period_data in df.items():
    for period, dataframe in period_data.items():

        if period == 'Daily':
            dataframe['is_daily'] = True
            dataframe['is_weekly'] = True
            dataframe['is_monthly'] = True

        elif period == 'Weekly':
            dataframe['is_daily'] = False
            dataframe['is_weekly'] = True
            dataframe['is_monthly'] = True

        elif period == 'Monthly':
            dataframe['is_daily'] = False
            dataframe['is_weekly'] = False
            dataframe['is_monthly'] = True

        desired_columns_order = ['Date', 'Title', 'Link','is_daily', 'is_weekly', 'is_monthly']
        dataframe = dataframe[desired_columns_order]

        dfs.append(dataframe.assign(Ticker=ticker, Period=period))

merged_df = pd.concat(dfs, ignore_index=True)

filtered_df = merged_df.drop_duplicates(subset=['Ticker', 'Title'])

filtered_df.loc[:, 'Date'] = filtered_df['Date'].astype(str)

filtered_df.loc[:, 'is_daily'] = filtered_df['is_daily'].astype(str).str.lower()
filtered_df.loc[:, 'is_weekly'] = filtered_df['is_weekly'].astype(str).str.lower()
filtered_df.loc[:, 'is_monthly'] = filtered_df['is_monthly'].astype(str).str.lower()

values = [tuple(row) for row in filtered_df[['Date', 'Ticker', 'Title', 'is_daily', 'is_weekly', 'is_monthly']].values]

def insert_rows(values):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute('DELETE FROM headlines')
        conn.commit()

        query = '''
        INSERT INTO headlines (publication_timestamp, ticker, headline, is_daily, is_weekly, is_monthly)
        VALUES (%s, %s, %s, %s, %s, %s)
        '''

        for value in values:
            cur.execute(query, value)
            print(value)

        conn.commit() 

    except Exception as e:
        print("An error occurred:", e)
        if conn:
            conn.rollback()  

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

num_threads = 8
chunk_size = len(values) // num_threads + 1
value_chunks = [values[i:i+chunk_size] for i in range(0, len(values), chunk_size)]

with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [executor.submit(insert_rows, chunk) for chunk in value_chunks]
    for future in futures:
        future.result()
