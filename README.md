# SMOOD
SMood is a sentiment analysis web application for S&P 500 stocks using PyTorch, Transformers, React, Axios and Redux.
## 1. Introduction
In today's dynamic financial world, staying ahead in the stock market requires a lot of different skills. It demands insight of previous trends, foresight on future trends, and an understanding of the market sentiment. To make the task a lot more easier, we introduce **SMOOD**, a comprehensive stock sentiment analysis app designed to aid investors, market analysts, researchers, businesses and financial advisors with practical insights derived from the collective mood of the market.
<br>
<br>
SMOOD uses the power of FinBERT, a LLM and an extension of the BERT model for financial tasks to gauge the market sentiment of a stock in financial markets. It analyzes the news headlines from various sources and predicts the **“mood”** of a market. A positive sentiment reflects the market is bullish, or has an optimistic outlook. Conversely, a negative sentiment reflects the bearish or pessimistic outlook of the market, expecting a drop in stock prices. If the sentiment does not change, it reflects the neutral nature of a stock’s market position. This can help those working in the finance or business domain to make informed decisions.
<br>
## 2. Background of Existing Systems
Sentiment Analysis is a technique that finds its application in various areas, including recommender systems, financial markets, social media monitoring among others. 
Some existing approaches to tackling the problem of financial market sentiment analysis includes lexicon-based approach, which relies on predefined sentiment dictionaries. Textual data is analyzed by matching words from the lexicon to those in the text and aggregating sentiment scores.
<br>
<br>
Machine Learning-based approaches have become more popular in recent years, due to the availability of tools and frameworks. Classification algorithms such as Support Vector Machines (SVM), Logistic Regression, Naive-Bayes, Decision Trees and Random Forests have been used to predict sentiment for simple use cases.
<br>
<br>
Deep Learning approaches have also seen their use for sentiment analysis of stock markets in recent years. Traditional deep learning models such as RNNs and LSTMs have been employed for sentiment analysis of large datasets. Transformer-based models such as BERT (Bidirectional Encoder Representations from Transformers) have also proven to be useful as they are pre-trained in most use cases but can also be leveraged for custom preferences, employing transfer learning.

## 3. Problem Statement
In today’s ever-changing landscape of financial markets, accurately gauging and measuring market feedback is a crucial skill for any investor, financial advisor, trader or market researcher. However, since the advent of the internet the data has grown exponentially in size. Therefore, it is difficult to analyze the vast majority of news, twitter posts and financial reports to make an accurate decision. Manual analysis of the data in this way can lead to errors, bias or overheads, because the nature of capital markets is dynamic and prone to change quickly. Hence, there is an ever-growing need for automated market sentiment analysis systems that can efficiently process and analyze large volumes of textual data to provide timely and actionable insights into market sentiment trends and their potential impact on market movements. 
<br>
## 4. Objectives
SMood aims to achieve the following objectives:
-	**Automated Sentiment Analysis:** SMood will be able to perform automated sentiment analysis over a period to provide market sentiment of a stock using Natural Language Processing techniques.
- **Real-Time Analysis:** SMood will analyze the data in real-time over a specific period, ensuring that it captures the market sentiment with maximum possible accuracy.
-	**Sentiment Classification:** SMood will collect news headlines and analyze it for sentiments, classifying it into positive, negative or neutral sentiments.
-	**Contextualization:** It also displays the key news and events that influence the sentiment of the market.
## 5. Proposed Solution
To solve the problem, we propose the transformer-based approach using the FinBERT model. It is a pre-trained Transformer model that was further trained on large financial corpus and serves as the backbone of the application. The model has been pre-trained by researchers on huge amounts of data and can form context and relationship between words. We then fine-tune the FinBERT model as needed to tailor it for our financial application.
<br>
<br>
Using the FinBERT model, we can accurately predict market sentiment by aggregating the individual sentiments. This is especially useful in our case, as traditional methods either rely excessively on training data, or prove to not be capturing complex patterns. Thus our proposed solution is the optimal balance between the Machine Learning-based and Deep Learning-based approaches and also a more sophisticated choice of technique.
## 6. Proposed Workflow
The proposed workflow for the project can very broadly be divided into following phases:
### 6.1 Data Science Phase
The process starts with the fetching of individual stock tickers listed on the S&P 500 index. These are fetched from [Slickcharts.com](https://www.slickcharts.com/), and stored in Supabase instance for later retrieval. 
<br>
<br>
After the collection of stock tickers, the tickers are used to fetch headlines via the [FinVizFinance API](https://pypi.org/project/finvizfinance/). These headlines are sorted in terms of daily, weekly and monthly news and stored in the database. 
<br>
<br>
Next up, the FinBERT model is fine-tuned on semi-supervised data by first applying [FinVADER](https://github.com/PetrKorab/FinVADER) to assign pseudo-labels on small subset of the dataset. These labels are then used for fine-tuning the base model. Results showed significant performance improvement for financial sentiment analysis, up to 10x on financial phrasebank data.
<br>
<br>
This model is then used to infer the sentiment on the headlines stored in the database and then update the sentiments of each headlines, as well as the aggregated sentiments of each company over daily, weekly and monthly periods.
