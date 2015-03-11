import twitter
import pymongo
import json


# Auth for Twitter
def oauth_login():



    # Define Auth
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    # Define Twitter API
    twitter_api = twitter.Twitter(auth=auth)

    return twitter_api

# define world bounding box
geoBoxWorld = "-180,-90,180,90"


twitterAccess = oauth_login()

twitter_stream = twitter.TwitterStream(auth=twitterAccess.auth)

stream = twitter_stream.statuses.filter(locations=geoBoxWorld)

for tweet in stream:
    print tweet['text']
    print tweet['user']['location']
    print tweet['created_at']
    print "_______________" * 8

    geo = tweet['geo']

    if geo and geo['type'] == 'Point':
        coords = geo['coordinates']

        print coords

    print "________________" * 8

    with open('outputs/formattedJSONTest.txt', 'a+') as streamTest:
        streamTest.write(json.dumps(tweet, indent=4))
        streamTest.write('_______________________________' * 8)