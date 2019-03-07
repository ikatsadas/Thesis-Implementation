import sys
import tweepy
from pymongo import MongoClient
import numpy as np
import collections
import json
from bson.json_util import loads
from bson.json_util import dumps as bsondumps

#This script gets the 10 most retweeted tweets of certain accounts and it saves those tweet-chains in mongoDB

ACCESS_TOKEN = sys.argv[3]
ACCESS_SECRET = sys.argv[4]
CONSUMER_KEY = sys.argv[1]
CONSUMER_SECRET = sys.argv[2]

auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

api = tweepy.API(auth,retry_count=10, retry_delay=5, retry_errors=set([103]), wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

client = MongoClient('localhost', 27017)
db = client['nameDB']

# load accounts
data = np.loadtxt("fake_news.txt", dtype=str)
all_users = data[:, :]

def getAlreadyExaminedUsers():
    allUsersExamined=[]
    i=0
    for og_tweet_collection in db.collection_names():
        if og_tweet_collection != "users_info":
            try:
                tweet = api.get_status(og_tweet_collection)
                userID=str(tweet.user.id)
                if userID not in allUsersExamined:
                    allUsersExamined.append(userID)
            except:
                collection = db[og_tweet_collection]
                cursor = collection.find({})
                if cursor.count() ==0:
                    print("the folowing tweet id has a problem", og_tweet_collection)
                    i=i+1
                else:
                    retweet=cursor.next()
                    jsonDumpsTweet=bsondumps(retweet)
                    jsonDumpsTweet = loads(jsonDumpsTweet)
                    userID=str(jsonDumpsTweet["retweeted_status"]["user"]["id"])
                    if userID not in allUsersExamined:
                        allUsersExamined.append(userID)
                pass
    print "In total,",i,"tweets where not available now."
    print "There have been examined",len(allUsersExamined)," users already."
    return allUsersExamined

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


examinedUsers=getAlreadyExaminedUsers()
for user in all_users:
    tweet_ids = []
    my_dict = {}
    if user[1] not in examinedUsers:
        print user[0], "has never been examined!"
        mylist=[]
        get_recent_tweets(user[1])

        # make a dictionary
        for item in mylist:
            datajson = json.dumps(item._json)
            datajson=json.loads(datajson)
            my_dict.update({datajson["id_str"]: datajson["retweet_count"]})

        d = collections.Counter(my_dict)

        # 10 most common (i.e. most retweeted)
        for k, v in d.most_common(10):
            print (k, v)
            get_retweets(k)
        print
    else:
        print user[0],"had already been examined!"
