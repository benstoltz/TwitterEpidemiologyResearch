import pymongo
import csv


# Function to search collection based on a query

def load_from_mongo(mongo_db, mongo_db_coll, return_cursor=False, criteria=None, projection=None, **mongo_conn_kw):

    # Can use critera and projection to limit the data that is returned
    # look at http://docs.mongodb.org/manual/reference/method/db.collection.find/

    # Can use MongoDB's aggregations framework for more detailed queries

    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]

    tweet_iterator = coll.find()
    print tweet_iterator
    with open('geoworld.csv', 'wb') as geoworldFile:
        my_file_writer = csv.writer(geoworldFile)
        my_file_writer.writerow(['date', 'latitude', 'longitude'])
        for tweet in tweet_iterator:
            date = tweet['date_tweeted']
            latitude = tweet['coordinates']['coordinates'][1]
            longitude = tweet['coordinates']['coordinates'][0]
            my_file_writer.writerow([date, latitude, longitude])





load_from_mongo('geoWorldStreamDatabase', 'geolocated')




