import nltk
import feedparser
import pandas as pd
from nltk.corpus import stopwords
from pymongo import MongoClient

def analysis(url1):
    feed = feedparser.parse(url1)

    #cols = ['Title','Summary']

    fox_df = pd.DataFrame()

    for item in feed['items']:
        fox_df = fox_df.append({
            'Title':item['title'],
            'Summary':item['summary'],
            'Source':'Fox News',
            'Link':item['link'],
            'Published Date':item['published']}, ignore_index = True)

    #data cleaning

    #remove puctuation
    fox_df['Summary'] = fox_df['Summary'].str.replace('[^\w\s]','', regex = False)

    #lower casing
    fox_df['Summary'] = fox_df['Summary'].apply(lambda x: " ".join(x.lower() for x in x.split()))

    #remove stopwords
    stWords = stopwords.words('english')
    fox_df['Summary'] = fox_df['Summary'].apply(lambda x: " ".join(x for x in x.split() if x not in stWords))

    #filtering by length of string
    fox_df = fox_df[fox_df['Summary'].str.len()>3]

    #sentiment analysis
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyser = SentimentIntensityAnalyzer()

    SentiList = []

    for row in fox_df['Summary']:
        vs = analyser.polarity_scores(row)
        SentiList.append(vs)
        
    Senti_df = pd.DataFrame(SentiList)
    Senti_df.head()

    #concat dataframes
    data_df = pd.concat([fox_df.reset_index(drop = True), Senti_df], axis =1)

    data_df['Sentiment'] = data_df['compound'].apply(lambda score : 'Positive' if score >= 0.01 else 'Negative' if score <= 0.01 else 'Neutral')

    data_df['words'] = data_df['Summary'].apply(lambda li : li.split(' '))

    #connection to MongoDB

    data_dict = data_df.to_dict('records')

    client = MongoClient("mongodb+srv://Dhruval:dhru9824900962@cluster0.5wprs.mongodb.net/SDM3?ssl=true&ssl_cert_reqs=CERT_NONE")
    db = client['SDM3']

    collection = db['Fox News']
    collection.insert_many(data_dict)
    print("Success")

    data_df.to_csv("Data.csv", header = True, index = False)



url1 = "http://feeds.foxnews.com/foxnews/latest"
analysis(url1)