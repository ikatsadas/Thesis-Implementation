import tweepy
import os
import sys
import time
from pymongo import MongoClient
import networkx as nx


client = MongoClient('localhost', 27017)
fake = 'getMostRetweetedFake'
real = 'getMostRetweetedTest'
db = client[real]

ACCESS_TOKEN = sys.argv[3]
ACCESS_SECRET = sys.argv[4]
CONSUMER_KEY = sys.argv[1]
CONSUMER_SECRET = sys.argv[2]
auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

api = tweepy.API(auth, retry_count=10, retry_delay=5, retry_errors=set([103]), wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)




def extract_information_for_users(stop):
    try:
        db.create_collection('users_info')  # creates a collection with user's id
    except:
        print ("The users_info collection existed allready")
    collectionName = db['users_info']
    for og_tweet_collection in db.collection_names(): # initialize the all_users set, to avoid examining users that have already been examined
        print ("for the ", og_tweet_collection)
        if og_tweet_collection == "users_info":
            print("in the users_info")
            #get the current list of users and init it to the set
            collection = db[og_tweet_collection]
            cursor = collection.find({"all_the_users_list": {"$exists": True}})
            for doc in cursor:
                print("in the all_the_users_list loop")
                dict = doc["all_the_users_list"]
                print dict
                for key in dict.keys():
                    print ("key: ",key)
            #for every user that is passed to the db until now do the following
            cursor = collection.find({"specific_tweet_id": {"$exists": True}})
            for doc in cursor:
                print ("in the spec id loop")
                dict = doc["specific_tweet_id"]
                print ("dictionary from spec id ", dict)
                for key in dict.keys():
                    print ("key: ",key)
                    print("value: ",dict.get(str(key)))
                    l=[]
                    l=dict.get(str(key))
                    print ("the new list ",l)
                    print ("type-the new list ", type(l))
                    print("type-value: ", type(dict.get(str(key))))
                #get the friends followers
                #save this info to the db
    # c = 0
    # for og_tweet_collection in db.collection_names():  # for every tweet
    #     if og_tweet_collection != "users_info":
    #         user_set_of_a_tweet = set()
    #         c = c + 1
    #         if c > stop:
    #             break
    #         collection = db[og_tweet_collection]
    #         cursor = collection.find({})  # Gets the tweets in that topic
    #         user_connections = []
    #         tweet = api.get_status(og_tweet_collection)
    #         user_connections.append(tweet.user.id)
    #         user_set_of_a_tweet.add(tweet.user.id)  # add the user to the specific tweet's user set
    #         # get all the users on this tweet-chain
    #         for document in cursor:
    #             id = document["user"]["id"]
    #             user_connections.append(id)
    #         if len(user_connections) > 1:  # if the tweet had retweets
    #             i = 0
    #             for k in user_connections:  # for every user involved
    #                 user_set_of_a_tweet.add(k)  # add the user to the specific tweet's user set
    #                 if str(k) not in user_set:  # if we havent examined this user
    #                     # for every user_id get friends and followers
    #                     user_followers = get_followers(k, c, i, len(user_connections))
    #                     user_friends = get_friends(k, c, i, len(user_connections))
    #                     user_set.add(str(k))  # add that user to the general user set (EXAMINED)
    #                     # SAVE TO DB
    #                     user_dict = {}
    #                     user_dict["friends"]=user_friends
    #                     user_dict["followers"] = user_followers
    #                     allthe_users[str(k)] = user_dict
    #                 i = i + 1
    #             spec_tweet_id= {og_tweet_collection: list(user_set_of_a_tweet)}
    #             if specifictweetid_flag_exists:
    #                 #update query (updating the existing document to that collection)
    #                 name='specific_tweet_id.'+og_tweet_collection
    #                 for i in list(user_set_of_a_tweet):
    #                     collectionName.update_one({'specific_tweet_id': {"$exists": True}},
    #                                           {'$push': {name:i}})
    #                 # {'$push': {'specific_tweet_id': spec_tweet_id}})
    #             else:
    #                 #create query (inserting the document to that collection)
    #                 collectionName.insert_one({"specific_tweet_id": spec_tweet_id})
    #         else:
    #             c = c - 1
    # if alltheuserslist_flag_exists:
    #     # update query (updating the existing document to that collection)
    #     for i in allthe_users.keys():
    #         name='all_the_users_list.'+str(i)
    #         collectionName.update_one({'all_the_users_list': {"$exists": True}},
    #                                   # {'$push': {'all_the_users_list': allthe_users}})
    #                                   {'$set': {name: allthe_users.get(str(i))}})
    # else:
    #     # create query (inserting the document to that collection)
    #     collectionName.insert_one({"all_the_users_list": allthe_users})

import traceback
def emailThis(to, subject="", body="", files=[]):
    try:
        fro = "ykatsadas@gmail.com"
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email.mime.text import MIMEText
        from email.utils import COMMASPACE, formatdate
        from email import encoders
        msg = MIMEMultipart()
        msg['From'] = fro
        msg['To'] = to
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        msg.attach(MIMEText(body))
        for file in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(file, "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
            msg.attach(part)
        smtp = smtplib.SMTP("smtp.gmail.com",587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(fro,sys.argv[5])#remove for git
        smtp.sendmail(fro, to, msg.as_string())
        smtp.close()
        return True
    except: traceback.print_exc()


try:
    # graph_generation(90)
    extract_information_for_users(90)
    emailThis("johnkats5896@gmail.com", subject="Script finished", body="The script has finished, chech the log file for more info")
    # graph_generation(1)
except:
    emailThis("johnkats5896@gmail.com",subject="Crash Report",body="Check the script")


