import json
import pymongo
import pandas as pd
import matplotlib.pyplot
from time import gmtime, mktime, strptime



def load_from_mongo(mongo_db, mongo_db_coll, return_cursor=False, criteria=None, projection=None, **mongo_conn_kw):

    # Can use critera and projection to limit the data that is returned
    # look at http://docs.mongodb.org/manual/reference/method/db.collection.find/

    # Can use MongoDB's aggregations framework for more detailed queries

    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]

    tweet_iterator = coll.find()
    print tweet_iterator

    rows_list = []
    now = mktime(gmtime())
    for tweet in tweet_iterator:
        author = ""
        rtauthor = ""

        # if a retweet get both original author and the retweeter

        try:
            author = tweet['user']['screen_name']
            rtauthor = tweet['retweeted_status']['user']['screen_name']

        except:
            try:
                author = tweet['user']['screen_name']
            except:
                continue

        reply_to = ""

        if tweet['in_reply_to_screen_name'] != 'null':
           reply_to = tweet['in_reply_to_screen_name']

        age = int(now - mktime(strptime(tweet['user']['account_created'], "%a %b %d %H:%M:%S +0000 %Y")) / (60 * 60 * 24))
        followers = tweet['user']['followers_count']

        dict1 = {}
        dict1.update({'author': author, 'retweet_of': rtauthor, 'reply_to': reply_to, 'age': age, 'followers': followers})
        rows_list.append(dict1)

    tweets = pd.DataFrame(rows_list)
    print tweets


load_from_mongo('geoWorldGraphVisDatabase', 'tweets')