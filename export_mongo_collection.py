from pymongo import MongoClient
import tweepy
import sys
import numpy as np

#This script prints the current state of the DB in mongo because compass and shell are inconvenient and can provide a scatter plot

client = MongoClient('localhost', 27017)
fake = 'getMostRetweetedFake'
real = 'getMostRetweeted3'
db = client[fake]

ACCESS_TOKEN = sys.argv[3]
ACCESS_SECRET = sys.argv[4]
CONSUMER_KEY = sys.argv[1]
CONSUMER_SECRET = sys.argv[2]
auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

api = tweepy.API(auth, retry_count=10, retry_delay=5, retry_errors=set([103]), wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

collectionName = db['users_info']
print("________________all the users list________________")
cursor = collectionName.find({"all_the_users_list": {"$exists": True}})
for doc in cursor:
    dict = doc["all_the_users_list"]
    counter=0
    for key in dict.keys():
        counter=counter+1
    print ("there are : ",counter,"users processed")
print("________________spec tweed id________________")
cursor = collectionName.find({"specific_tweet_id": {"$exists": True}})
count_id=0
total=0
for doc in cursor:#for every document
    print("     id: ",count_id)
    dict = doc["specific_tweet_id"]
    # if count_id != 0:#if it isn't the first document to examine
    #     #it does the same thing as the "else" as far as I'm concerned
    #     counter=0
    #     for key in dict.keys():
    #         counter=counter+1
    #     print ("            there are : ",counter)
    #     for key in dict.keys():
    #         l=[]
    #         l=dict.get(str(key))
    #         print("     --containing: ",len(l))
    #         total=total+len(l)
    # else:
    #this gives the number of tweets that are in this document
    print ("            there are : ", len(dict))
    for item in dict:#for every tweet in the document
        for k in item.keys():#there should be only one entry anyway (its more convenient to use for-loop)
            l=[]
            l=item.get(str(k))
            #this gives the number of users for that tweet
            print("     --containing: ", len(l))
            total = total + len(l)
    count_id=count_id+1
print("_________________________________________________")
print ("Total of: ",total)

#######################Suspended Users Check###############################
data = np.loadtxt("real_news.txt", dtype=str)
all_users = data[:, :]
#for every user who made an original tweet (from the file)
counter=0
for user in all_users:
    #count the users who have been suspended
    try:
        api.get_user(int(user[1]))
    except:
        counter=counter+1
print "________________________________________________"
print "There are ",counter, "suspended/inactive users"
print "And ",len(all_users)-counter,"active users"
###########################################################################

#######################Check number of retweets gathered###################
#for every tweet
#   if it exists
#       get the original tweet info
#   else
#       if it has retweets
#           get from the retweets gathered the maximum retweet count recorded of the original
#       else
#           move to the next tweet and count it as loss
#   get the number of the retweets that are gathered in the db
#   print the two numbers and the difference
#   add the difference in an array and maybe plot it
#print the number of losses and the number of ok collections
###########################################################################


#######################################
#       FIX THE STRUCTURE
# cursor = collectionName.find({"specific_tweet_id": {"$exists": True}})
# list=[]
# for doc in cursor:
#     dict = doc["specific_tweet_id"]
#     list.append(dict)
# collectionName.insert_one({"specific_tweet_id": list})

