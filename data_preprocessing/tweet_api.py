# Import the Twython class
from twython import Twython
import json
import os
import pandas as pd
from tqdm import tqdm

try:
    os.remove('twitter_dataset.csv')
except OSError:
    pass

def main():
    old_df = pd.read_csv('data/twitter_dataset_2.csv', lineterminator='\n')
    #first load the dictonary with the top used english words
    with open('improved_dict.txt') as d:
        word_list = d.read()

    words = word_list.split('\n')


    # Dictonary structure with the fields that we are interested in acquire from the tweets
    dict_ = {'user': [],
             'text': [],
             'hashtags': [],
             'mentions': []
             }


    # Instantiate an object
    python_tweets = Twython('9Tz9FnZ1PR9AcEvudwC7hqOod', #API Key
                            'Z7upFmGJZE3oAfcb2ZUmRdEeBJJkkYTQ86PuB3iKgWqXFdMFNo') #API Secret


    #each query has a target word
    queries = []
    for w in words:
        query = {'q': w, #the query word
                'result_type': 'recent',
                'count': 100, #100 tweets, which is the maximum limit admitted by Twitter
                'lang': 'en', #we are interested only in english tweets
                }
        queries.append(query)

    #perform the queries to get the tweet and map the JSON in our dictonary
    for q in tqdm(queries[:50]):
        for status in python_tweets.search(**q)['statuses']:
            dict_['user'].append(status['user']['screen_name']) #username
            dict_['text'].append(status['text']) #content of the tweet

            #this is necessary cuz the hashtags may be null or there can be more than one
            #this can easily be done with this magical regular expression
            ht = [d['text'] for d in status['entities']['hashtags'] if 'text' in d] #list of hashtags
            dict_['hashtags'].append(ht)

            #same thing for the mentions
            ment = [d['screen_name'] for d in status['entities']['user_mentions'] if 'screen_name' in d] #list of mentions
            dict_['mentions'].append(ment)

    # Structure data in a pandas DataFrame for easier manipulation
    df = pd.DataFrame(dict_)

    df = df.append(old_df)
    df.to_csv('data/twitter_dataset_2.csv', index=False, encoding='utf-8')

if __name__ == '__main__':
    main()
    from time import sleep
    while True:
        sleep(1200)
        main()
