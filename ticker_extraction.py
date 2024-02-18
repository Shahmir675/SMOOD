import psycopg2
import requests
import os
import pandas as pd
from finvizfinance.quote import finvizfinance
from io import StringIO

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

url = 'https://www.slickcharts.com/sp500'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

response = requests.get(url, headers=headers)
html_content = StringIO(response.text)

tables = pd.read_html(html_content)

sp500_table = tables[0]

companies, tickers = sp500_table['Company'], sp500_table['Symbol']
tickers = [ticker.replace('.', '-') for ticker in tickers]

data = list(zip(tickers, companies))

delete_query = "DELETE FROM Stocks"
insert_query = "INSERT INTO Stocks (Ticker, Stock_Name) VALUES (%s, %s)"

conn = get_connection()
cur = conn.cursor()

try:
    cur.execute(delete_query)
    cur.executemany(insert_query, data)
    conn.commit()
    print("Data insertion successful.")
except Exception as e:
    conn.rollback()
    print("Error:", e)
finally:
    cur.close()
    conn.close()
