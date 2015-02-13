import twitter
import json


# Auth for Twitter
def oauth_login():
    CONSUMER_KEY = 'igqW4Q8nN1uCTatbSlGspddjz'
    CONSUMER_SECRET = 'BMbCbBS5rkJl2Hk7Yf37Q5DJVvAV5GybTC2txUqrqAmJKt9pT9'
    OAUTH_TOKEN = '477055521-8m4V7Ky4wGaMEKBeCPeeJy2Mf6iADrmIvCfoS5v2'
    OAUTH_TOKEN_SECRET = 'Mj5QpSObqw35A2W3IFGS4qct6ZA7plLelCG0OpyI17ZVa'

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