# -*- coding: UTF-8 -*-
# !/usr/bin/env python

import tweepy
import json
from pymongo import MongoClient
import requests
import re
import sys

#This script was meant to stream tweets from certain accounts (has not been implemented further)

consumer_key = sys.argv[1]
consumer_secret = sys.argv[2]
access_token = sys.argv[3]
access_token_secret = sys.argv[4]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

try:
    redirect_url = auth.get_authorization_url()
    print ('Connected successfully to Twitter.')
except tweepy.TweepError:
    print ('Error! Failed to get request token.')

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

            # ----CHECK-------------
            created_at = datajson['created_at']
            # print out a message to the screen that we have collected a tweet
            print("Tweet collected at " + str(created_at))
            print('The user  said: ')
            print (datajson['text'])
            # ----------------------

            collection = db["collection_" + 'hashtag']  # needs topic
            # insert the data into the mongoDB into a collection called collection_'hashtag' (topic)
            # if the collection doesn't exist, it will be created.
            # this example only keeps 10 tweets
            # we should stop based on the frequenxy of the tweets (the topic stoped trending)
            self.num_tweets += 1
            if self.num_tweets < 11:
                collection.insert(datajson)
                return True
            else:
                self.num_tweets = 0
                return False
        except Exception as e:
            print(e)


# Listener on specific accounts (fact-checking organisations) for keyword extraction
class StreamListenerKeywords(tweepy.StreamListener):

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
            print ("GOT NEW TWEET")
            # Decode the JSON from Twitter
            datajson = json.loads(data)
            url = 'http://api.cortical.io/rest/text/keywords?retina_name=en_associative'
            if "https://" not in datajson['text']:  # if the is no link in the tweet then search for keywords in tweet
                text = datajson['text'].encode('utf-8')
            else:  # if there is a link search for keywords on the page
                text = re.findall('"(https?://.*?)"', datajson['text'])
            headers = {'content-type': 'application/json', 'api-key': '129b8d60-e298-11e7-9586-f796ac0731fb'}
            r = requests.post(url, data=text, headers=headers)

            # checks
            print (r.status_code)
            print (json.loads(r.text))

            # needs to save the keywords to use them!

            # 1) gets topics
            keywords = json.dumps(r.text)
            for key in keywords:
                print (type(key))
                for tweet in tweepy.Cursor(api.search, q=unicode(key,"utf-8"), lang="en").items():
                    collection = db["collection_" + 'hashtag']  # needs topic
                    datajson = json.dumps(tweet)
                    collection.insert(datajson)
            print("Tracking: " + str(keywords))
            # 2) start stream-listener for that topic
            listener = StreamListenerCollector(api)
            streamer = tweepy.Stream(auth=auth, listener=listener)
            streamer.filter(languages=["en"], track=keywords, async=True)  # async to run on a new thread


        except Exception as e:
            print(e)



# start stream-listener
listOfFCAccounts = ['3451884743']  # list of fact checking accounts (has my user id)
listener = StreamListenerKeywords(api)
sampler = tweepy.Stream(auth=auth, listener=listener)
sampler.filter(languages=["en"], follow=listOfFCAccounts, async=True)  # async to run on a new thread
