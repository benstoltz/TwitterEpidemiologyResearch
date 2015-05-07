import sys
import time
from urllib2 import URLError
from httplib import BadStatusLine
import twitter
import pymongo
import json


def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):

    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):

        if wait_period > 3600:  # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e
        # See https://dev.twitter.com/overview/api/response-codes for codes
        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (not authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (not found)'
            return None
        elif e.e.code == 429:
            print >> sys.stderr, 'Encountered 429 Error (rate limit exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, 'Retrying in 15 minutes...ZzZzZzZz...'
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZzZ...Awake and trying again.'
                return 2
            else:
                raise e  # Caller must handle the rate limiting error
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

        # End of nested helper function

    wait_period = 2
    error_count = 0

    while True:
        try:
            print "frank"
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise


def save_to_mongo(data, mongo_db, mongo_db_collection):
    # Connects to the MongoDB server running on
    # localhost: 27017 by default

    # Get a reference to a particular database

    db = client[mongo_db]

    # Reference a particular collection in the database

    coll = db[mongo_db_collection]

    # Perform a bulk insert and return the IDs

    return coll.insert(data)


def oauth_login():
    OAUTH_TOKEN = '477055521-PpCBhLezySPX8CWmSCyUxRmQU7AMZyB5PqyvPNJF'
    OAUTH_TOKEN_SECRET = 'PdPH2nrikeBGiHlfg3vm2dWys6knZSQYYMvnF5xFKy14G'
    CONSUMER_KEY = 'eqOV0Iu2M1114ILJW87nHMoxX'
    CONSUMER_SECRET = '8Gg7KoKpcRJlADXWRXb78PaaHcx6KAIU4Q4sxbeatC0Bpyf9gh'

    # Define Auth
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    # Define Twitter API
    twitter_api = twitter.Twitter(auth=auth)

    return twitter_api


def twitter_search(twitter_api, q, max_results=200, **kw):

    search_results = make_twitter_request(twitter_api.search.tweets, q=q, count=100, **kw)

    statuses = search_results['statuses']

    # Iterate through batches of results by following the cursor until we
    # reach the desired number of results, keeping in mind that OAuth users
    # can "only" make 180 search queries per 15-minute interval.
    # See limits for details.
    # Reasonable number of results is ~1000, although not all queries will return that number

    # Enforce limit
    max_results = min(100000, max_results)

    for _ in range(1000):  # 10 * 100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError, e:  # No more results when next_results doesn't exist
            print "Done here!"
            break

        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([kv.split('=') for kv in next_results[1:].split("&")])

        search_results = make_twitter_request(twitter_api.search.tweets, **kwargs)
        statuses += search_results['statuses']

        if len(statuses) > max_results:
            break
    return statuses

# Open mongoDB connection:

client = pymongo.MongoClient()

# Set up Oauth login
twitter_api = oauth_login()

# Create query
q = 'chikungunya'
# qtest = 'israel'

# Create response
responses = twitter_search(twitter_api, q, max_results=100000)

for response in responses:
    default = 'Null'
    tweet = {}
    tweet['text'] = response.get('text', default)
    tweet['in_reply_to_status_id'] = response.get('in_reply_to_status', default)
    tweet['id'] = response.get('id', default)
    tweet['favorite_count'] = response.get('favorite_count', default)
    tweet['in_reply_to_screen_name'] = response.get('in_reply_to_screen_name', default)
    tweet['in_reply_to_user_id'] = response.get('in_reply_to_user_id', default)
    tweet['retweet_count'] = response.get('retweet_count', default)
    tweet['favorited'] = response.get('favorited', default)
    # Start user object
    tweet['user'] = {}
    user = response.get('user', default)
    tweet['user']['id'] = user.get('id', default)
    tweet['user']['followers_count'] = user.get('followers_count', default)
    tweet['user']['listed_count'] = user.get('listed_count', default)
    tweet['user']['is_translation_enabled'] = user.get('is_translation_enabled', default)
    tweet['user']['utc_offset'] = user.get('utc_offset', default)
    tweet['user']['statuses_count'] = user.get('statuses_count', default)
    tweet['user']['description'] = user.get('description', default)
    tweet['user']['friends_count'] = user.get('friends_count', default)
    tweet['user']['location'] = user.get('location', default)
    tweet['user']['following'] = user.get('following', default)
    tweet['user']['geo_enabled'] = user.get('geo_enabled', default)
    tweet['user']['name'] = user.get('name', default)
    tweet['user']['lang'] = user.get('lang', default)
    tweet['user']['url'] = user.get('url', default)
    tweet['user']['account_created'] = user.get('created_at', default)
    tweet['user']['contributors_enabled'] = user.get('contributors_enabled', default)
    tweet['user']['timezone'] = user.get('timezone', default)
    tweet['user']['protected'] = user.get('protected', default)
    tweet['user']['default_profile'] = user.get('default_profile', default)
    tweet['user']['is_translator'] = user.get('is_translator', default)
    # End user
    # placeholder for geo
    tweet['possibly_sensitive'] = response.get('possibly_sensitive', default)
    tweet['lang'] = response.get('lang', default)
    tweet['tweet_created_at'] = response.get('created_at', default)
    # Start metadata
    tweet['metadata'] = {}
    tweet['metadata']['iso_language_code'] = response['metadata']['iso_language_code']
    tweet['metadata']['result_type'] = response['metadata']['result_type']

    if response['geo'] and response['geo']['type'] == 'Point':
        tweet['geo'] = response.get('geo', default)
        tweet['place'] = response.get('place', default)
        # print json.dumps(tweet, indent=1)
        save_to_mongo(tweet, 'chikungunyaDatabase', 'geolocated')
        # print "bob"
    else:
        # print json.dumps(tweet, indent=1)
        save_to_mongo(tweet, 'chikungunyaDatabase', 'tweets')
        # print "bob"