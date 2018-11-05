import tweepy
import os
import sys
import time
from pymongo import MongoClient
import networkx as nx
import random

#This script gets all the friends and followers of the users who were involved in a tweet chain and saves them to mongo appropriatly, in respect to the API's limitations  (both mongo and twitter)


client = MongoClient('localhost', 27017)
fake = 'getMostRetweetedFake'
real = 'getMostRetweeted3'
db = client[fake]

RTthreshold=500
mongoThresholdPerDoc=500000 #(actual 600000, but just in case of crashing we have 500K)

ACCESS_TOKEN = sys.argv[3]
ACCESS_SECRET = sys.argv[4]
CONSUMER_KEY = sys.argv[1]
CONSUMER_SECRET = sys.argv[2]
auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

api = tweepy.API(auth, retry_count=10, retry_delay=5, retry_errors=set([103]), wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)


def get_followers(user_id, tweetnumber, retweeter_num, total_retweeters):
    users = []
    page_count = 0
    try:
        for i, user in enumerate(tweepy.Cursor(api.followers_ids, id=user_id, count=5000).pages()):#gets 5000 users per page
            sys.stdout.write('\r')
            sys.stdout.write(
                'Getting page %i for followers, for user: %i, for tweet number: %i, number of retweeters %i / %i' % (
                    i, user_id, tweetnumber, retweeter_num, total_retweeters))
            sys.stdout.flush()
            users += user
            time.sleep(60)
    except tweepy.error.TweepError:
        print ("Error whilst geting the followers of user:", user_id)
    return users

def get_friends(user_id, tweetnumber, retweeter_num, total_retweeters):
    users = []
    page_count = 0
    try:
        for i, user in enumerate(tweepy.Cursor(api.friends_ids, id=user_id, count=5000).pages()):#gets 5000 users per page
            sys.stdout.write('\r')
            sys.stdout.write(
                'Getting page %i for friends, for user: %i, for tweet number: %i, number of retweeters %i / %i' % (
                    i, user_id, tweetnumber, retweeter_num, total_retweeters))
            sys.stdout.flush()
            users += user
            time.sleep(60)
    except tweepy.error.TweepError:
        print ("Error whilst geting the friends of user:", user_id)
    return users

def update_specTweetId(collectionName,numberOfDocumentsSpecificTweetId,spec_tweet_id):
    # update query (updating the existing document to that collection)
    collectionName.update_one({'specific_tweet_id': {"$exists": True}, 'No': numberOfDocumentsSpecificTweetId},
                              # {'$push': {name:spec_tweet_id}})
                              {'$push': {'specific_tweet_id': spec_tweet_id}})

def newDoc_specTweetId(collectionName,numberOfDocumentsSpecificTweetId,l):
    collectionName.insert_one({"specific_tweet_id": l, 'No': numberOfDocumentsSpecificTweetId})

def update_allTheUsersList(collectionName,numberOfDocuments,allthe_users,user_connections):
    # update query (updating the existing document to that collection)
    for i in user_connections:
        if allthe_users.get(str(i)) is not None:
            name = 'all_the_users_list.' + str(i)
            collectionName.update_one({'all_the_users_list': {"$exists": True}, 'No': numberOfDocuments},
                                      # {'$push': {'all_the_users_list': allthe_users}})
                                      {'$set': {name: allthe_users.get(str(i))}})

def newDoc_allTheUsersList(collectionName,numberOfDocuments,allthe_users,user_connections):
    # update index
    collectionName.update_one({'index': {"$exists": True}},
                              {'$set': {'index.numberOfDocuments': numberOfDocuments}})
    theCurrent={}
    for i in user_connections:
        if allthe_users.get(str(i)) is not None:
            theCurrent[str(i)]=allthe_users.get(str(i))
    # create query (inserting the document to that collection)
    collectionName.insert_one({"all_the_users_list": theCurrent, "No": numberOfDocuments})

def resetUsersInMemory(user_connections,allthe_users):
    # reset the usersInMemory
    usersInMemory = 0
    for i in user_connections:
        if allthe_users.get(str(i)) is not None:
            for k, v in allthe_users.get(str(i)).items():
                usersInMemory = usersInMemory + len(v)
    return usersInMemory

def extract_information_for_users(stop):
    # there is the need of an index document to keep track of the divisions of the other two documents
    # the divisions are done due to the existance of a 16MB limit per document that mongoDB has
    # Division: according to the all_the_users_list(since it gathers more info in size) after every 5 records are added it then moves on to a new document (to prevent reaching the limit)
    # _____________START OF INITALIZATION____________________
    try:
        db.create_collection('users_info')  # creates a collection with user's id
    except:
        print ("The users_info collection existed already")
    collectionName = db['users_info']

    index_exists = True
    if collectionName.find({'index': {"$exists": True}}).count() == 0:
        index_exists = False
    if not index_exists:
        print ("The Index document did not exist!")
        # create query (inserting the document to that collection)
        index = {}
        # should get the number of documents that already exist (if any)
        numberOfDocuments = collectionName.find({'all_the_users_list': {"$exists": True}}).count()
        index["numberOfDocuments"] = numberOfDocuments
        #limit of record per document
        index["limitOfRecordsInDocument"] = 1
        limitOfRecordsInDocument = 1
        collectionName.insert_one({"index": index})
        index_exists = True
    else:  # OK
        # get the nubers and set them (initialization)
        cursor = collectionName.find({"index": {"$exists": True}})
        for doc in cursor:
            index = doc["index"]
            limitOfRecordsInDocument = int(index["limitOfRecordsInDocument"])
            numberOfDocuments = int(index["numberOfDocuments"])
    user_set = set()  # to check if we have examined this user
    tweet_checked_set=set()
    allthe_users = {}  # will store the  user_dit{followers,firends} for each user to be saved in the DB
    # initialize the all_users set, to avoid examining users that have already been examined
    for og_tweet_collection in db.collection_names():
        if og_tweet_collection == "users_info":
            # get the current list of users and init it to the set
            collection = db[og_tweet_collection]
            cursor = collection.find({"all_the_users_list": {"$exists": True}})
            for doc in cursor:
                dict = doc["all_the_users_list"]
                for key in dict.keys():
                    user_set.add(str(key))
            cursor = collection.find({"specific_tweet_id": {"$exists": True}})
            for doc in cursor:
                dict=doc["specific_tweet_id"]
                for obj in dict:
                    for tweet in obj:
                        tweet_checked_set.add(str(tweet))
    #------------------------------------------------------------------
    #make the first documents (all_the_users_list, spec_tweet_id)
    indexChnaged = False
    usersInMemory=0
    l=[]
    user_connections=[]
    numberOfDocuments=numberOfDocuments+1
    numberOfDocumentsSpecificTweetId = numberOfDocuments
    newDoc_specTweetId(collectionName, numberOfDocumentsSpecificTweetId, l)
    newDoc_allTheUsersList(collectionName, numberOfDocuments, allthe_users,user_connections)
    # _____________END OF INITALIZATION______________________


    c = 0
    flag = True
    for og_tweet_collection in db.collection_names():  # for every tweet
        flag = True
        if og_tweet_collection != "users_info":  # to avoid examining the users_info collection
            collection = db[og_tweet_collection]
            cursor = collection.find({})  # Gets the tweets in that topic
            if cursor.count()<=RTthreshold:#retweet Threshold (found to be 500)- this is done in order to complete the research faster by narrowing down the collection
                user_set_of_a_tweet = set()
                c = c + 1
                if c > stop:
                    break
                user_connections = []
                needsToSave=False
                try:
                    tweet = api.get_status(og_tweet_collection)
                    user_connections.append(tweet.user.id)
                    user_set_of_a_tweet.add(tweet.user.id)  # add the user to the specific tweet's user set
                except:
                    flag = False
                    print("the folowing tweet id has a problem", og_tweet_collection)
                    pass
                if flag:  # if there is a problem with the original poster's account, dont examine anything for now
                    if og_tweet_collection not in tweet_checked_set:
                        # get all the users on this tweet-chain
                        for document in cursor:
                            id = document["user"]["id"]
                            user_connections.append(id)
                        if len(user_connections) > 1:  # if the tweet had retweets
                            i = 0
                            for k in user_connections:  # for every user involved
                                user_set_of_a_tweet.add(k)  # add the user to the specific tweet's user set
                                if str(k) not in user_set:  # if we havent examined this user
                                    needsToSave=True
                                    # for every user_id get friends and followers
                                    user_followers = get_followers(k, c, i, len(user_connections))
                                    user_friends = get_friends(k, c, i, len(user_connections))
                                    user_set.add(str(k))  # add that user to the general user set (EXAMINED)
                                    # SAVE TO DB
                                    user_dict = {}
                                    user_dict["friends"] = user_friends
                                    user_dict["followers"] = user_followers
                                    usersInMemory = usersInMemory + len(user_followers)+len(user_friends)#keep track of the users in memory
                                    allthe_users[str(k)] = user_dict
                                i = i + 1
                            spec_tweet_id = {og_tweet_collection: list(user_set_of_a_tweet)}
                            if not indexChnaged:
                                update_specTweetId(collectionName, numberOfDocumentsSpecificTweetId, spec_tweet_id)
                            else:
                                # create query (inserting the document to that collection)
                                l = []
                                l.append(spec_tweet_id)
                                numberOfDocumentsSpecificTweetId=numberOfDocumentsSpecificTweetId+1
                                newDoc_specTweetId(collectionName, numberOfDocumentsSpecificTweetId, l)
                                indexChnaged = False
                        else:
                            c = c - 1
                    if needsToSave:
                        if usersInMemory<=mongoThresholdPerDoc:
                            update_allTheUsersList(collectionName, numberOfDocuments, allthe_users, user_connections)
                        else:
                            # make a sub-user_connections array so that they dont exceed the limit in order to update the old doc
                            # -we can calculate how many users there are already in the previous doc and how many we have in the memory left to add
                            usersInMemory_ALL = usersInMemory
                            # reset the usersInMemory
                            usersInMemory =resetUsersInMemory(user_connections,allthe_users)
                            #-at this point: usersInMemory_InTheOldDoc has how many users there are in the old Doc and usersInMemory has how many users we need to save
                            #-we substract to see how many users we can fit in the old document according to the limit
                            usersAlreadysavedInThePreviousDoc=abs(usersInMemory_ALL-usersInMemory)
                            usersLeftToFit=mongoThresholdPerDoc-usersAlreadysavedInThePreviousDoc
                            #-we split the users so that we can update the old document with as many as they can fit
                            usersPending=0
                            usersPendingList=[]
                            for i in user_connections:
                                foll=[]
                                frie=[]
                                if allthe_users.get(str(i)) is not None:
                                    for k, v in allthe_users.get(str(i)).items():
                                        if k=="friends":
                                            frie=v
                                        elif k=="followers":
                                            foll=v
                                    if usersPending+len(foll)+len(frie)<=usersLeftToFit:
                                        usersPendingList.append(i)
                                        user_connections.remove(i)
                                        usersPending=usersPending + len(foll) + len(frie)
                            # update the previous document
                            update_allTheUsersList(collectionName, numberOfDocuments, allthe_users, usersPendingList)
                            # keep making a sub-user_connections array so that they dont exceed the limit in order to create new document(s)
                            # reset the usersInMemory
                            usersInMemory = resetUsersInMemory(user_connections,allthe_users)
                            # print "_________________________________________________"
                            # print "PART2: usersInMemory", usersInMemory, "len(user_connections)", len(user_connections)
                            while(usersInMemory>mongoThresholdPerDoc):#if and while the users that are left to be saved are more than the limit
                                # print "---PART2: usersInMemory", usersInMemory, "len(user_connections)", len(user_connections)
                                usersPending = 0
                                usersPendingList = []
                                for i in user_connections:
                                    foll = []
                                    frie = []
                                    if allthe_users.get(str(i)) is not None:
                                        for k, v in allthe_users.get(str(i)).items():
                                            if k == "friends":
                                                frie = v
                                            elif k == "followers":
                                                foll = v
                                        if usersPending + len(foll) + len(frie) <= mongoThresholdPerDoc:
                                            usersPendingList.append(i)
                                            user_connections.remove(i)
                                            usersPending = usersPending + len(foll) + len(frie)
                                #-make the new doc with the sub-array of the user_connections
                                # print "---PART2: (before the update) usersPending", usersPending, "len(usersPendingList)", len(usersPendingList)
                                numberOfDocuments = numberOfDocuments + 1
                                newDoc_allTheUsersList(collectionName, numberOfDocuments, allthe_users,usersPendingList)
                                usersInMemory=resetUsersInMemory(user_connections, allthe_users)
                            #continue by saving what is left in a new doc (should be less than the limit)
                            # print "_________________________________________________"
                            # print "PART3: usersInMemory", usersInMemory,"len(user_connections)",len(user_connections)
                            numberOfDocuments=numberOfDocuments+1
                            indexChnaged=True
                            newDoc_allTheUsersList(collectionName, numberOfDocuments, allthe_users,user_connections)

def graph_generation(stop):
    # for each tweet add the user id as a node
    G = nx.Graph()
    collection = db["users_info"]
    cursor = collection.find({"all_the_users_list": {"$exists": True}})
    # for doc in cursor:
    #     all_the_users=doc["all_the_users_list"]
    #     print type(all_the_users)
    #     print all_the_users
    #     a=all_the_users["0"]
    #     print "a"
    #     print type(a)
    #     print a["friends"]
    # c = 0
    # for og_tweet_collection in db.collection_names():  # for every tweet
    #     c = c + 1
    #     if c > stop:
    #         break
    #     collection = db[og_tweet_collection]
    #     cursor = collection.find({})  # Gets the tweets in that topic
    #     user_connections = []
    #     tweet = api.get_status(og_tweet_collection)
    #     user_connections.append(tweet.user.id)
    #     # get all the retweets
    #     for document in cursor:
    #         id = document["user"]["id"]
    #         user_connections.append(id)
    #     if len(user_connections) > 1:  # if the tweet had retweets
    #         G.add_nodes_from(user_connections)  # set people who retweeted this as nodes
    #         i = 0
    #         for k in user_connections:
    #             if i != 0:  # if it is not the original poster
    #                 # TO DO: get the inf from the DB
    #                 G.add_edge(user_connections[0], k)  # add it as a node
    #                 for j in user_connections:
    #                     if k != j:
    #                         if j in user_followers or j in user_friends:
    #                             G.add_edge(j, k)  # if there is a connection between friends/followers add the edge
    #             i = i + 1
    #         nx.draw(G)
    #         plt.show()
    #     else:
    #         c = c - 1

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
        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(fro, sys.argv[5])  # remove for git
        smtp.sendmail(fro, to, msg.as_string())
        smtp.close()
        return True
    except:
        traceback.print_exc()

message = "This process had the pid: " + str(os.getpid())
try:
    print ("This process has the pid", os.getpid())
    emailThis("johnkats5896@gmail.com", subject="Script Started",
              body="The script has starteded, check the log file for more info!" + message)
    # extract_information_for_users(90)
    # emailThis("johnkats5896@gmail.com", subject="Script pt 1 finished", body="The first part of the script has finished, chech the log file for more info! Now it will continue to the next segment!" + message)
    db = client[real]
    extract_information_for_users(300)
    emailThis("johnkats5896@gmail.com", subject="Script finished",
              body="The script has finished, check the log file for more info!" + message)
except:
    traceback.print_exc()
    emailThis("johnkats5896@gmail.com", subject="Crash Report",
              body="Check the script!" + message + "\n" + traceback.format_exc())
