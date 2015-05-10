import pymongo
import vincent
import pandas
import operator
import geocoder
import csv
import json
import re
from datetime import datetime, timedelta
from email.utils import parsedate_tz
from nltk.corpus import stopwords
from nltk import bigrams
import string
from collections import Counter
from collections import defaultdict



# Function to convert the Twitter date/time String

def to_datetime(time):
    time_tuple = parsedate_tz(time.strip())
    dt = datetime(*time_tuple[:6])
    return str(dt - timedelta(seconds=time_tuple[-1]))

punctuation = list(string.punctuation)
stop = stopwords.words('english') + stopwords.words('spanish') + punctuation + ['rt', 'via', "I'm", 'da', 'q',
                                                                                'que', 'no', 'mas', 'pra', 'a', 'like',
                                                                                'com', 'um', 'na', 'gt', 'lt', 'eu', 'vou']
com = defaultdict(lambda : defaultdict(int))

emoticons_str = r"""
    (?:
        [:=;]   # Eyes
        [oO\-]? # Nose
        [D\)\]\(\]/\\OpP]   #  Mouth
    )"""

regex_str = [
    emoticons_str,
    r'<[^>]+>',  # HTML tags
    r'(?:@[\w_]+)',  # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs

    r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
    r'(?:[\w_]+)',  # other words
    r'(?:\S)'  # anything else
]

tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)


def tokenize(s):
    return tokens_re.findall(s)

def preprocess(s, lowercase=False):
    tokens = tokenize(s)

    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens



# Function to search collection based on a query

def load_from_mongo(mongo_db, mongo_db_coll, return_cursor=False, criteria=None, projection=None, **mongo_conn_kw):

    # Can use critera and projection to limit the data that is returned
    # look at http://docs.mongodb.org/manual/reference/method/db.collection.find/

    # Can use MongoDB's aggregations framework for more detailed queries

    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]

    dates = []
    tweet_iterator = coll.find()
    count_terms = Counter()
    count_hash = Counter()
    count_mentions = Counter()
    count_only = Counter()
    for tweet in tweet_iterator:
        # create a list with all terms
        terms = [term for term in preprocess(tweet['text'].encode('ascii', 'ignore').decode('ascii')) if term not in stop]
        terms_hash = [term for term in preprocess(tweet['text'].encode('ascii', 'ignore').decode('ascii')) if term.startswith('#')]
        terms_mentions = [term for term in preprocess(tweet['text'].encode('ascii', 'ignore').decode('ascii')) if term.startswith('@')]
        # terms_only = [term for term in preprocess(tweet['text'].encode('ascii', 'ignore').decode('ascii')) if term not in stop and not term.startswith(('#', '@'))]
        terms_bigrams = bigrams(terms)
        if '#Jaramillo900k' in terms_hash:
            dates.append(tweet['date_tweeted'])

        # update the counter
        count_terms.update(terms)
        count_hash.update(terms_hash)
        count_mentions.update(terms_mentions)
        count_only.update(terms_bigrams)

        #extract locations
        tweetLatitude = tweet['coordinates']['coordinates'][1]
        tweetLongitude = tweet['coordinates']['coordinates'][0]

    print count_only.most_common(30)

    # bar chart to visualize hash
    hash_freq = count_hash.most_common(15)
    labels, freq = zip(*hash_freq)
    data = {'data': freq, 'x': labels}
    bar = vincent.Bar(data, iter_idx='x')
    bar.to_json('hash_freq.json')

    # bar chart to visualize mentions
    mentions_freq = count_mentions.most_common(15)
    labels, freq = zip(*mentions_freq)
    data = {'data': freq, 'x': labels}
    bar = vincent.Bar(data, iter_idx='x')
    bar.to_json('mentions_freq.json')







load_from_mongo('geoWorldStreamDatabase', 'geolocated')