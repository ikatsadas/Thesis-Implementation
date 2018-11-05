import sys
import tweepy
from pymongo import MongoClient
import numpy as np
import collections
import json


ACCESS_TOKEN = sys.argv[3]
ACCESS_SECRET = sys.argv[4]
CONSUMER_KEY = sys.argv[1]
CONSUMER_SECRET = sys.argv[2]

auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

api = tweepy.API(auth,retry_count=10, retry_delay=5, retry_errors=set([103]), wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

client = MongoClient('localhost', 27017)
db = client['getMostRetweetedFake']

# load accounts
# data = np.loadtxt("C:/Users/johnk/Desktop/thesis/remoteDevelopment/fake_news.txt", dtype=str)
data = np.loadtxt("fake_news.txt", dtype=str)
all_users = data[:, :]


def get_retweets(initial_id):
    try:
        db.create_collection(str(initial_id))  # creates a collection with tweet's id
    except:
        print ("This ID existed!")
        # if it aleady exist say how much you had before
        collected = db[str(initial_id)].count()
        print ("Collection is already created. It has ", collected, " tweets")
    # pagination
    print ("Created new collection for that ID!")
    for p in range(1, 33):
        print
        print ("page number ", p)
        rts = api.retweets(int(initial_id), count=100, page=p)
        rt_counter = 1

        if len(rts) == 0:
            break

        # for every tweet that we got: add it to mongo and print the result
        for tweet in rts:
            db[str(initial_id)].insert_one(tweet._json)
            sys.stdout.write('\r')
            sys.stdout.write("Retweets %i out of %i" % (rt_counter, len(rts)))
            sys.stdout.flush()
            rt_counter += 1



mylist=[]
def get_recent_tweets(target):
    print ("getting tweets...")
    hashtags = []
    mentions = []
    tweet_count = 0
    for status in tweepy.Cursor(api.user_timeline, id=target).items():
        tweet_count += 1
        mylist.append(status)
        if(tweet_count>3200): #3200
            break


for user in all_users:
    tweet_ids = []
    my_dict = {}
    #mylist = db[user[1]].find({})  # get ALL the tweets from that user (that are saved)
    mylist=[]
    # print type(user[1])
    get_recent_tweets(user[1])

    # make a dictionary
    for item in mylist:
        datajson = json.dumps(item._json)
        datajson=json.loads(datajson)
        my_dict.update({datajson["id_str"]: datajson["retweet_count"]})

    d = collections.Counter(my_dict)

    # 5 most common (i.e. most retweeted)
    for k, v in d.most_common(10):
        print (k, v)
        get_retweets(k)
    print
