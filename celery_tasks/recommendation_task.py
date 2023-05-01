from typing import List

from celery import shared_task

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import joblib, re


@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='book_recommendation:predict_recommendation')
def predict_recommendation(self, title:str):

    # df = pd.read_csv('data/twitter_data.csv')
    df = pd.read_csv('data/Books.csv')
    df.columns = ['target', 'tweet_id', 'time', 'flag', 'user', 'text']

    features ='text'
    target = 'target'

    df = df[[features, target]]

    df['target'] = pd.to_numeric(df['target'], downcast='integer')

    df['target'] = df['target'].replace(4, 1)
    df['target'].value_counts()

    # take out the @usernames
    df['text'] = df['text'].apply(lambda x: re.sub('@[^\s]+','',x))

    # take out the links
    df["text"] = df["text"].apply(lambda x: re.sub(r"http\S+", "", x))

    # take out the hashtags
    df["text"] = df["text"].apply(lambda x: re.sub(r"#\S+", "", x))


    X_train, X_test, y_train, y_test = train_test_split(df["text"], df["target"], test_size=0.2, random_state=42)

    vectorizer = TfidfVectorizer()
    X_train = vectorizer.fit_transform(X_train)
    X_test = vectorizer.transform(X_test)

    lr = LogisticRegression()
    lr.fit(X_train, y_train)
    lr_score = lr.score(X_test, y_test)
    print(lr_score)

    mnb = MultinomialNB()
    mnb.fit(X_train, y_train)
    mnb_score = mnb.score(X_test, y_test)
    print(mnb_score)

    model = None
    if mnb_score > lr_score:
        model = mnb
    else:
        model = lr
    print(model)

    #Save Model
    joblib.dump(model, 'model.pkl')
    print('Dump model success')

    clf = joblib.load('model.pkl')

    vect = vectorizer.transform([tweet])
    pred = clf.predict(vect)

    sentiment  = ''
    if pred == 1:
        sentiment = 'positive'
    else:
        sentiment = 'negative'

    return sentiment
