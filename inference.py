## Importing Dependencies
import psycopg2
import os
import pandas as pd
import torch
from transformers import BertForSequenceClassification, BertTokenizer
from tqdm.notebook import tqdm
from concurrent.futures import ThreadPoolExecutor
## Connecting to Supabase
def get_connection():
    try:
        connection = psycopg2.connect(
            dbname='postgres',
            user='postgres.mlelytyghqgzaunwuwnp',
            password='SMOODCUSIT@',
            host='aws-0-us-west-1.pooler.supabase.com',
            port='5432',
        )

    except psycopg2.OperationalError as e:
        print(f'Error: {e}')
        return None

    else:
        print('Connected Established!')
        return connection
conn = get_connection()
## Extracting headlines
def extract_headlines():
    with conn.cursor() as curr:
        curr.execute("SELECT * FROM headlines")
        headlines = curr.fetchall()
        columns = [curr.description[i][0] for i in range(len(curr.description))]
        df = pd.DataFrame(headlines, columns=columns)
    return df

headlines = extract_headlines()
headlines.head(10)
## Loading model and tokenizer
tokenizer = BertTokenizer.from_pretrained(r'models\tokenizer')
model = BertForSequenceClassification.from_pretrained(r'models\finetuned_finbert')
X = headlines['headline']
encodings = tokenizer(X.tolist(), truncation=True, padding=True)
## Preparing dataset
class Dataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        item = {key : torch.tensor(val[idx]) for key, val in self.encodings.items()}
        return item
    
    def __len__(self):
        return len(self.encodings['input_ids'])
dataset = Dataset(encodings)
## Predicting sentiments
def analyze_sentiment(dataset):
    model.eval()
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=8)

    predictions = []
    probabilities = []

    with torch.no_grad():
        for batch in tqdm(dataloader, desc='Sentiment Analysis', unit="batch"):
            input_ids = batch['input_ids']
            attention_mask = batch['attention_mask']

            with torch.no_grad():
                outputs = model(input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                probabilities_batch = torch.softmax(logits, dim=1)
                predicted_labels_batch = torch.argmax(probabilities_batch, dim=1)
            
            predictions.extend(predicted_labels_batch.tolist())
            probabilities.extend(probabilities_batch.tolist())

    return predictions, probabilities
predicted, probabilities = analyze_sentiment(dataset)
label_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
predicted_sentiments = [label_map[label] for label in predicted]
data = {'headline': X.tolist(), 'sentiment': predicted_sentiments}
results = pd.DataFrame(data)
results
## Updating sentiments for individual headlines 
def update_headlines(rows):
    try:
        with conn.cursor() as curr:
            data = [(row['sentiment'], row['headline']) for _, row in rows.iterrows()]
            curr.executemany("UPDATE headlines SET sentiment = %s WHERE headline = %s", data)
        return True
    except Exception as e:
        print(f"Error updating headline: {e}")
        return False
with tqdm(total=len(results), desc="Updating headlines", unit="rows") as pbar:
    for _, row in results.iterrows():
        update_headlines(pd.DataFrame([row]).copy())
        pbar.update(1)
    
conn.commit()
## Aggregating sentiments for stocks across multiple time periods
def extract_headlines():
    with conn.cursor() as curr:
        curr.execute("SELECT * FROM headlines")
        headlines = curr.fetchall()
        columns = [curr.description[i][0] for i in range(len(curr.description))]
        df = pd.DataFrame(headlines, columns=columns)
    return df
df = extract_headlines()
grouped = df.groupby(['ticker', 'is_daily', 'is_weekly', 'is_monthly'])

aggregated_sentiments = {}
for group, data in grouped:
    ticker, is_daily, is_weekly, is_monthly = group
    sentiment_counts = data['sentiment'].value_counts()
    predominant_sentiment = sentiment_counts.idxmax()
    aggregated_sentiments.setdefault(ticker, {})[(is_daily, is_weekly, is_monthly)] = predominant_sentiment
def aggregate_sentiments_by_company(headlines):
    aggregated_sentiments = {}

    for _, row in headlines.iterrows():
        ticker = row['ticker']

        if ticker not in aggregated_sentiments:
            aggregated_sentiments[ticker] = {}

        period = (row['is_daily'], row['is_weekly'], row['is_monthly'])
        sentiment = row['sentiment']

        aggregated_sentiments[ticker][period] = sentiment

    return aggregated_sentiments
def update_stocks_table(aggregated_sentiments):
    with conn.cursor() as cursor:
        for ticker, sentiments in aggregated_sentiments.items():
            daily_sentiment = sentiments.get((True, True, True), None)
            weekly_sentiment = sentiments.get((False, True, True), None)
            monthly_sentiment = sentiments.get((False, False, True), None)

            if daily_sentiment is None:
                daily_sentiment = weekly_sentiment if weekly_sentiment is not None else monthly_sentiment
            if weekly_sentiment is None:
                weekly_sentiment = monthly_sentiment if monthly_sentiment is not None else daily_sentiment
            if monthly_sentiment is None:
                monthly_sentiment = weekly_sentiment if weekly_sentiment is not None else daily_sentiment

            cursor.execute("UPDATE stocks SET daily_sentiment = %s, weekly_sentiment = %s, monthly_sentiment = %s WHERE ticker = %s",
                                (daily_sentiment, weekly_sentiment, monthly_sentiment, ticker))
            print(f"Updated sentiments for Ticker: {ticker}")
        
    conn.commit()
    print("Sentiments updated successfully.")
update_stocks_table(aggregated_sentiments)
