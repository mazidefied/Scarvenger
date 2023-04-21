from google_play_scraper import app, Sort, reviews_all
from app_store_scraper import AppStore
import pandas as pd
import numpy as np
import json, os, uuid

try:
    num_reviews = int(input("Enter the number of reviews to scrape: "))

    app_store = input("Enter the name of the app on App Store: ")
    app_id = input("Enter the app ID on App Store: ")
    play_store = input("Enter the package name of the app on Play Store: ")

    print("Retrieving Google Play Store reviews...")
    g_reviews = reviews_all(
            play_store,
            sleep_milliseconds=0, # defaults to 0
            lang='en', # defaults to 'en'
            country='us', # defaults to 'us'
            sort=Sort.NEWEST, # defaults to Sort.MOST_RELEVANT
        )[:num_reviews]
    print(f"Retrieved {len(g_reviews)} Google Play Store reviews")

    print("Retrieving App Store reviews...")
    a_reviews = AppStore('us', app_store, app_id)
    a_reviews.review()
    print(f"Retrieved {len(a_reviews.reviews)} App Store reviews")

    print("Processing and cleaning data...")
    g_df = pd.DataFrame(np.array(g_reviews),columns=['review'])
    g_df2 = g_df.join(pd.DataFrame(g_df.pop('review').tolist()))

    g_df2.drop(columns={'userImage', 'reviewCreatedVersion'},inplace = True)
    g_df2.rename(columns= {'score': 'rating','userName': 'user_name', 'reviewId': 'review_id', 'content': 'review_description', 'at': 'review_date', 'replyContent': 'developer_response', 'repliedAt': 'developer_response_date', 'thumbsUpCount': 'thumbs_up'},inplace = True)
    g_df2.insert(loc=0, column='source', value='Google Play')
    g_df2.insert(loc=3, column='review_title', value=None)
    g_df2['language_code'] = 'en'
    g_df2['country_code'] = 'us'

    a_df = pd.DataFrame(np.array(a_reviews.reviews),columns=['review'])
    a_df2 = a_df.join(pd.DataFrame(a_df.pop('review').tolist()))

    a_df2.drop(columns={'isEdited'},inplace = True)
    a_df2.insert(loc=0, column='source', value='App Store')
    a_df2['developer_response_date'] = None
    a_df2['thumbs_up'] = None
    a_df2['language_code'] = 'en'
    a_df2['country_code'] = 'us'
    a_df2.insert(loc=1, column='review_id', value=[uuid.uuid4() for _ in range(len(a_df2.index))])
    a_df2.rename(columns= {'review': 'review_description','userName': 'user_name', 'date': 'review_date','title': 'review_title', 'developerResponse': 'developer_response'},inplace = True)
    a_df2 = a_df2.where(pd.notnull(a_df2), None)

    result = pd.concat([g_df2,a_df2])
    result.to_csv('app_reviews.csv', index=False)

    print("Data cleaning and processing complete.")
    print(f"{len(result)} total reviews saved to 'app_reviews.csv'.")
    
except Exception as e:
    print(f"An error occurred: {str(e)}")
