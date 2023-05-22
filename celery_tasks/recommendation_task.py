from typing import List

from celery import shared_task

import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import joblib, re
from scipy.sparse.linalg import svds
from fastapi import HTTPException
from sklearn.metrics.pairwise import cosine_similarity 


from dotenv import load_dotenv
from supabase import create_client



load_dotenv() 
SUPABASE_URL = os.getenv('supabase_url')
SUPABASE_KEY = os.getenv('supabase_key')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 1},
             name='book_recommendation:predict_recommendation')
def predict_recommendation(self, title:str):

    books = pd.read_csv('data/Books.csv')
    # print('berhasil baca books')
    users = pd.read_csv("data/Users.csv")
    # print('berhasil baca users')
    ratings = pd.read_csv("data/Ratings.csv")
    # print('berhasil baca ratings')


    books.dropna(inplace=True)

    ratings_with_name = ratings.merge(books,on='ISBN')

    ratings_with_name.drop(columns=["ISBN","Image-URL-S","Image-URL-M"],axis=1,inplace=True)
    # print('dapet ratings_with_name')

    complete_df = ratings_with_name.merge(users.drop("Age", axis=1), on="User-ID")
    complete_df['Location'] = complete_df['Location'].str.split(',').str[-1].str.strip()
    # print('dapet complete_df')


    num_rating_df = complete_df.groupby('Book-Title').count()['Book-Rating'].reset_index()
    num_rating_df.rename(columns={'Book-Rating': 'num_ratings'}, inplace=True)
    # print('dapet num_rating_df')

    x = complete_df.groupby('User-ID').count()['Book-Rating']>200
    knowledgable_users = x[x].index
    # print('dapet x dan knowledgable_users')

    filtered_rating = complete_df[complete_df['User-ID'].isin(knowledgable_users)]
    # print('filtered_rating')


    y = filtered_rating.groupby('Book-Title').count()['Book-Rating']>=50
    famous_books = y[y].index
    # print('dapet y')

    if title in famous_books:
        # print('masuk famous_books handle')
        final_ratings =  filtered_rating[filtered_rating['Book-Title'].isin(famous_books)]
        
        pt = final_ratings.pivot_table(index='Book-Title',columns='User-ID'
                            ,values='Book-Rating')
        pt.fillna(0,inplace=True)
        # print('dapet pt')
        

        similarity_score = cosine_similarity(pt)

        recommendations = recommend(title, books, similarity_score, pt)
    else:
        # print('masuk NON famous_books handle')

        books_df = books[['Book-Title', 'Book-Author', 'Publisher','ISBN']]
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        book_profiles = tfidf_vectorizer.fit_transform(
            books_df['Book-Title'] + ' ' + books_df['Book-Author'] + ' ' + books_df['Publisher']
        )

        recommendations = recommend_books(title, tfidf_vectorizer, book_profiles, books_df)

    return {'recommendations':recommendations}

def recommend(book_title, books, similarity_score, pt):
    # print('masuk recommend')
    index = np.where(pt.index==book_title)[0][0]
    similar_books = sorted(list(enumerate(similarity_score[index])),key=lambda x:x[1], reverse=True)[1:6]
    
    data = []
    
    for i in similar_books:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        # item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['ISBN'].values))
        
        data.append(item)
    return data

def recommend_books(book_title, tfidf_vectorizer, book_profiles, books_df ,top_n=5):
    user_profile = tfidf_vectorizer.transform([book_title])

    # Calculate cosine similarity between user profile and all book profiles
    similarities = cosine_similarity(user_profile, book_profiles).flatten()

    # Get the indices of books that have the same title as the user input
    duplicate_indices = [i for i, book in enumerate(books_df['Book-Title']) if book.lower() == book_title.lower()]

    # Exclude the duplicate indices from the similarities array
    similarities[duplicate_indices] = -1

    # Sort books based on similarity scores and get top N recommendations
    top_indices = similarities.argsort()[::-1][:top_n]
    recommended_books = books_df.iloc[top_indices]

    recommended_books_list = []
    for book_id in recommended_books.index:
        book_info = {
            'title': books_df.loc[book_id, 'Book-Title'],
            # 'author': books_df.loc[book_id, 'Book-Author'],
            'isbn': books_df.loc[book_id, 'ISBN'],
        }
        recommended_books_list.append(book_info)

    return recommended_books_list