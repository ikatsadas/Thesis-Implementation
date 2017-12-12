import tweepy
import json
from pymongo import MongoClient

# Connection with Twitter
consumer_key = 'd4Sb0mUcvxc5d8YQBEYw8WPvD'
consumer_secret = '1kvxbAPlRD99GU19gTeBbqMKCAuZcQ4x68dzRipzJVpK0PUTCj'
access_token = '3451884743-1s8M0J5iFkMuC2Urr3YzUsXtkaY8a5xuqjdjCCG'
access_token_secret = 'GuoIHbguIGoblzU1IG7kkGYiU45kK6A2En80Ycc5a6Gzt'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

try:
    redirect_url = auth.get_authorization_url()
    print 'Connected successfully to Twitter.'
except tweepy.TweepError:
    print 'Error! Failed to get request token.'

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Connection with MongoDB
client = MongoClient('localhost', 27017)
db = client['twitter_db']


# stream classes
class StreamListenerCollector(tweepy.StreamListener):
    # This is a class provided by tweepy to access the Twitter Streaming API.

    def on_connect(self):
        self.num_tweets = 0
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")

    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False

    def on_data(self, data):
        try:

            # Decode the JSON from Twitter
            datajson = json.loads(data)

            #----CHECK-------------
            created_at = datajson['created_at']
            # print out a message to the screen that we have collected a tweet
            print("Tweet collected at " + str(created_at))
            print('The user  said: ')
            print datajson['text']
            #----------------------

            collection = db["collection_" + hashtag]
            # insert the data into the mongoDB into a collection called collection_'hashtag' (topic)
            # if the collection doesn't exist, it will be created.
            #this example only keeps 10 tweets
            #we should stop based on the frequenxy of the tweets (the topic stoped trending)
            self.num_tweets += 1
            if self.num_tweets < 11:
                collection.insert(datajson)
                return True
            else:
                self.num_tweets = 0
                return False
        except Exception as e:
            print(e)

# class StreamListenerSampler(tweepy.StreamListener):
#     # This is a class provided by tweepy to access the Twitter Streaming API.
#
#     def on_connect(self):
#         self.num_tweets = 0
#         # Called initially to connect to the Streaming API
#         print("You are now connected to the streaming API.")
#
#     def on_error(self, status_code):
#         # On error - if an error occurs, display the error / status code
#         print('An Error has occured: ' + repr(status_code))
#         return False
#
#     def on_data(self, data):
#         try:
#
#             # Decode the JSON from Twitter
#             datajson = json.loads(data)
#
#         except Exception as e:
#             print(e)



while(true):
    # start stream-listener
    # listener = StreamListenerSampler(api)
    # sampler = tweepy.Stream(auth=auth, listener=listener)
    # sampler.filter(languages=["en"])

    #1) gets a topic
    #2) start stream-listener for that topic
    listener = StreamListenerCollector(api)
    streamer = tweepy.Stream(auth=auth, listener=listener)
    streamer.filter(languages=["en"], track=[topic])
