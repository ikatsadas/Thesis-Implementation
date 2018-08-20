from pymongo import MongoClient
import tweepy
import sys

client = MongoClient('localhost', 27017)
fake = 'getMostRetweetedFake'
real = 'getMostRetweetedTest'
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
    print ("there are : ",counter)
print("________________spec tweed id________________")
cursor = collectionName.find({"specific_tweet_id": {"$exists": True}})
count_id=0
total=0
for doc in cursor:
    print("     id: ",count_id)
    dict = doc["specific_tweet_id"]
    if count_id != 0:
        counter=0
        for key in dict.keys():
            counter=counter+1
        print ("            there are : ",counter)
        for key in dict.keys():
            l=[]
            l=dict.get(str(key))
            print("     --containing: ",len(l))
            total=total+len(l)
    else:
        print ("            there are : ", len(dict))
        for item in dict:
            for k in item.keys():
                l=[]
                l=item.get(str(k))
                print("     --containing: ", len(l))
                total = total + len(l)
    count_id=count_id+1
print("_________________________________________________")
print ("Total of: ",total)


#######################################
#       FIX THE STRUCTURE
# cursor = collectionName.find({"specific_tweet_id": {"$exists": True}})
# list=[]
# for doc in cursor:
#     dict = doc["specific_tweet_id"]
#     list.append(dict)
# collectionName.insert_one({"specific_tweet_id": list})

