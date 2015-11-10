import pymongo
import csv
from datetime import datetime, timedelta
from email.utils import parsedate_tz

# Function to search collection based on a query

def to_datetime(time):
    time_tuple = parsedate_tz(time.strip())
    dt = datetime(*time_tuple[:6])
    return str(dt - timedelta(seconds=time_tuple[-1]))

def load_from_mongo(mongo_db, mongo_db_coll, return_cursor=False, criteria=None, projection=None, **mongo_conn_kw):

    # Can use critera and projection to limit the data that is returned
    # look at http://docs.mongodb.org/manual/reference/method/db.collection.find/

    # Can use MongoDB's aggregations framework for more detailed queries

    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]

    tweet_iterator = coll.find()
    print tweet_iterator
    with open('../outputs/stormTweets.csv', 'wb') as geoworldFile:
        my_file_writer = csv.writer(geoworldFile)
        my_file_writer.writerow(['screen_name', 'tweet_id', 'date', 'latitude', 'longitude', 'content'])
        for tweet in tweet_iterator:
            user_id = tweet['user']['screen_name'].encode('ascii', 'ignore').decode('ascii')
            tweet_id = tweet['id']
            date = to_datetime(tweet['date_tweeted'])
            latitude = tweet['coordinates']['coordinates'][1]
            longitude = tweet['coordinates']['coordinates'][0]
            content = tweet['text'].encode('ascii', 'ignore').decode('ascii')
            my_file_writer.writerow([user_id, tweet_id, date, latitude, longitude, content])


load_from_mongo('stormStreamDatabase', 'geolocated')




