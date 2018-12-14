#This script is to merge to similar collections in mongo (union)
import sys
import tweepy
from pymongo import MongoClient
import numpy as np
import collections
import json
from bson.json_util import loads
from bson.json_util import dumps as bsondumps


ACCESS_TOKEN = sys.argv[3]
ACCESS_SECRET = sys.argv[4]
CONSUMER_KEY = sys.argv[1]
CONSUMER_SECRET = sys.argv[2]

auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

api = tweepy.API(auth,retry_count=10, retry_delay=5, retry_errors=set([103]), wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)
client = MongoClient('localhost', 27017)
fake_news_users_file="fake_news.txt"
real_news_users_file="real_news.txt"
db1_name='getMostRetweeted2'
db2_name='getMostRetweetedTest'
db1 = client[db1_name]
db2=client[db2_name]

#___________SEE HOW MANY TWEETS BELONG TO EACH USER_______________
def first_test(excludeZeroCollections,filename,this_db):
    data = np.loadtxt(filename, dtype=str)
    all_users = data[:, :]

    numOfTweets=[]
    i=0
    for user in all_users:
        numOfTweets.append(0)
        i=i+1
    counter=0
    tweetchains=0
    deletedTweet=0
    notdeleted=0
    zeroRetweeets=0
    for og_tweet_collection in this_db.collection_names():
        if og_tweet_collection != "users_info":
            try:
                collection = this_db[og_tweet_collection]
                cursor = collection.find({})
                numOfTweetsInTHISCollection=cursor.count()
                tweet = api.get_status(og_tweet_collection)
                userID = str(tweet.user.id)
                i=0
                for user in all_users:
                    if userID == user[1]:
                        if excludeZeroCollections:
                            if numOfTweetsInTHISCollection!=0:
                                numOfTweets[i]=int(numOfTweets[i])+1
                            else:
                                zeroRetweeets=zeroRetweeets+1
                        else:
                            numOfTweets[i] = int(numOfTweets[i]) + 1
                    i=i+1
                notdeleted=notdeleted+1
            except:
                collection = this_db[og_tweet_collection]
                cursor = collection.find({})
                if cursor.count() == 0:
                    print("the folowing tweet id has a problem", og_tweet_collection)
                    counter=counter+1
                    zeroRetweeets=zeroRetweeets+1
                else:
                    retweet = cursor.next()
                    jsonDumpsTweet = bsondumps(retweet)
                    jsonDumpsTweet = loads(jsonDumpsTweet)
                    userID = str(jsonDumpsTweet["retweeted_status"]["user"]["id"])
                    i = 0
                    for user in all_users:
                        if userID == user[1]:
                            numOfTweets[i] = int(numOfTweets[i]) + 1
                        i = i + 1
                deletedTweet=deletedTweet+1
                pass
            tweetchains=tweetchains+1
    print "_________________FINAL RESULTS_________________________________________"
    i=0
    total=0
    for user in all_users:
        print user,numOfTweets[i]
        total=total+numOfTweets[i]
        i=i+1
    print counter, "collections had a problem"
    print "Tweet-chains num:",tweetchains
    print "Deleted tweets num:",deletedTweet
    print "notdeleted=",notdeleted
    if excludeZeroCollections:
        print "Tweet-chains with zero retweets:",zeroRetweeets
    print "total=",total

def db_to_dict(db_name,this_db):
    # Read all the tweet collections from the THIS_DB and then store them in a dictionary DICT_THIS
    print "initializing "+db_name+"..."
    dict_db={}
    for og_tweet_collection in this_db.collection_names():
        if og_tweet_collection != "users_info":
            collection = this_db[og_tweet_collection]
            cursor = collection.find({})
            list_of_retweets=[]
            for retweet in cursor:
                #fill the list of retweets with the json retweets
                list_of_retweets.append(retweet)
            #add this collection to the dictionary (og_tweet_collection:[list of retweets json])
            dict_db[og_tweet_collection]=list_of_retweets
    return dict_db

#_______________INITIALIZATION_____________
def initialization():
    dict_first=db_to_dict(db1_name,db1)
    dict_second=db_to_dict(db2_name,db2)
    #Create a blank dictionary were we will store the finalized collections of the final tweet
    dict_new={}
    return dict_first,dict_second,dict_new


def make_user_dict(this_db,dictionary):
    user_dict={}
    for collection in dictionary:
        try:
            tweet = api.get_status(collection)
            userID = str(tweet.user.id)
        except:
            col = this_db[collection]
            cursor = col.find({})
            if cursor.count() != 0:
                retweet = cursor.next()
                jsonDumpsTweet = bsondumps(retweet)
                jsonDumpsTweet = loads(jsonDumpsTweet)
                userID = str(jsonDumpsTweet["retweeted_status"]["user"]["id"])
        if userID not in user_dict:
            user_dict[userID]=1
        else:
            value=user_dict.get(userID)
            user_dict[userID]=int(value)+1
    return user_dict

#________________SECOND TESTS_____________
def second_test():
    #for every common collection print the number of tweets in that collection in DB1 and in DB2
    dict_first,dict_second,dict_new=initialization()
    commonCollections=0
    uniqueCollections1=0
    uniqueCollections2=0
    for collection in dict_first:
        if collection in dict_second:
            commonCollections=commonCollections+1
        else:
            uniqueCollections1=uniqueCollections1+1
    for collection in dict_second:
        if collection not in dict_first:
            uniqueCollections2=uniqueCollections2+1
    #print the number of the common collections
    #print the number of the unique collections in DB1
    #print the number of the unique collections in DB2
    print "Common collections number:",commonCollections
    print "Unique collections for the first:",uniqueCollections1
    print "Unique collections for the second:", uniqueCollections2
    #print for every user the number of tweet collections that "he" has in the DB1
    #print for every user the number of tweet collections that "he" has in the DB2
    print "FOR THE FIRST DB----------------------------------------------"
    first_test(excludeZeroCollections=False, filename=real_news_users_file, this_db=db1)
    print "FOR THE SECOND DB---------------------------------------------"
    first_test(excludeZeroCollections=False, filename=real_news_users_file, this_db=db2)
    print "--------------------------------------------------------------"
    #print the number of users involved in the DB1
    #print the number of users involved in the DB2
    db1_user_dict=make_user_dict(db1,dict_first)
    db2_user_dict = make_user_dict(db2,dict_second)
    print "Number of users in the first DB:",len(db1_user_dict)
    print "Number of users in the second DB:", len(db2_user_dict)




#___________UNION OF DBs PROCCESS_____________
#for every tweet collection in the DICT_SECOND
#   if that collection exists in the DICT_FIRST:
#       then compare the two: for every tweet that exists in the first one compare it with every other that exists in the other one
#       (UNION)
#       if the two tweets are the same then keep the document in the final tweet collection
#       if one document doesn't exist in the other collection then keep it in the final collection
#       add the name of that collection of the dictionary(that was just added in the final) to an array ARR_DONE
#   if the collection doesn't exist in the dictionary:
#       add the collection as is in the final db
#   for ever collection in the dictionary:
#       if the collection is not in the ARR_DONE array:
#           add the collection as is to the final dictionary

#_________SAVING PROCCESS__________
#create the new database
#for every tweet collection:
#   create the collection
#   for every tweet in the collection:
#       add the tweet in that collection in the db as a document





#_____________FINAL TESTS___________
#print the number of collections in the final db and the number of retweets in them
#print the number of users involved in the db
#print for every user the number of tweet collections that "he" has






#EXECUTION
# first_test(excludeZeroCollections=True,filename=fake_news_users_file,this_db=db1)
# initialization()
# second_test()
collection = db2["users_info"]
cursor = collection.find({"all_the_users_list": {"$exists": True}})
all_the_users={}
for doc in cursor:
    all_the_users.update(doc["all_the_users_list"])


empty_user=0
for user in all_the_users:
    u=all_the_users.get(user)
    print u
    if len(u["friends"])==0 and len(u["followers"])==0:
        empty_user=empty_user+1

print "there are",empty_user,"empty users out of",len(all_the_users)