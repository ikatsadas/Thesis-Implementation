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


def get_followers(user_id, tweetnumber, retweeter_num, total_retweeters):
    users = []
    page_count = 0
    try:
        for i, user in enumerate(tweepy.Cursor(api.followers_ids, id=user_id, count=200).pages()):
            sys.stdout.write('\r')
            sys.stdout.write(
                'Getting page %i for followers, for user: %i, for tweet number: %i, number of retweeters %i / %i' % (
                    i, user_id, tweetnumber, retweeter_num, total_retweeters))
            sys.stdout.flush()
            users += user
            time.sleep(60)
    except tweepy.error.TweepError:
        print "Error whilst geting the followers of user:",user_id
    return users


def get_friends(user_id, tweetnumber, retweeter_num, total_retweeters):
    users = []
    page_count = 0
    try:
        for i, user in enumerate(tweepy.Cursor(api.friends_ids, id=user_id, count=200).pages()):
            sys.stdout.write('\r')
            sys.stdout.write(
                'Getting page %i for friends, for user: %i, for tweet number: %i, number of retweeters %i / %i' % (
                    i, user_id, tweetnumber, retweeter_num, total_retweeters))
            sys.stdout.flush()
            users += user
            time.sleep(60)
    except tweepy.error.TweepError:
        print "Error whilst geting the friends of user:",user_id
    return users


def extract_information_for_users(stop):
    try:
        db.create_collection('users_info')  # creates a collection with user's id
    except:
        print ("The users_info collection existed allready")
    collectionName = db['users_info']

    alltheuserslist_flag_exists=True
    if collectionName.find({'all_the_users_list': {"$exists": True}}).count() == 0:
        alltheuserslist_flag_exists=False
        print False
    specifictweetid_flag_exists = True
    if collectionName.find({'specific_tweet_id': {"$exists": True}}).count() == 0:
        specifictweetid_flag_exists = False
        print False

    time.sleep(10)


    user_set = set()  # to check if we have examined this user
    allthe_users = {}  #wil store the  user_dit{followers,firends} for each user to be saved in the DB
    for og_tweet_collection in db.collection_names(): # initialize the all_users set, to avoid examining users that have already been examined
        if og_tweet_collection == "users_info":
            #get the current list of users and init it to the set
            collection = db[og_tweet_collection]
            cursor = collection.find({"all_the_users_list": {"$exists": True}})
            for doc in cursor:
                dict = doc["all_the_users_list"]
                for key in dict.keys():
                    user_set.add(str(key))
    c = 0
    for og_tweet_collection in db.collection_names():  # for every tweet
        if og_tweet_collection != "users_info":
            user_set_of_a_tweet = set()
            c = c + 1
            if c > stop:
                break
            collection = db[og_tweet_collection]
            cursor = collection.find({})  # Gets the tweets in that topic
            user_connections = []
            tweet = api.get_status(og_tweet_collection)
            user_connections.append(tweet.user.id)
            user_set_of_a_tweet.add(tweet.user.id)  # add the user to the specific tweet's user set
            # get all the users on this tweet-chain
            for document in cursor:
                id = document["user"]["id"]
                user_connections.append(id)
            if len(user_connections) > 1:  # if the tweet had retweets
                i = 0
                for k in user_connections:  # for every user involved
                    if(i==6):#JUST FOR TESTING
                        user_set_of_a_tweet.add(k)  # add the user to the specific tweet's user set
                        if str(k) not in user_set:  # if we havent examined this user
                            # for every user_id get friends and followers
                            user_followers = get_followers(k, c, i, len(user_connections))
                            # user_friends = get_friends(k, c, i, len(user_connections))
                            user_set.add(str(k))  # add that user to the general user set (EXAMINED)
                            # SAVE TO DB
                            user_dict = {}
                            # user_dict["friends"]=user_friends
                            user_dict["followers"] = user_followers
                            allthe_users[str(k)] = user_dict
                    i = i + 1
                spec_tweet_id= {og_tweet_collection: list(user_set_of_a_tweet)}
                if specifictweetid_flag_exists:
                    #update query (updating the existing document to that collection)
                    name='specific_tweet_id.'+og_tweet_collection
                    for i in list(user_set_of_a_tweet):
                        collectionName.update_one({'specific_tweet_id': {"$exists": True}},
                                              {'$push': {name:i}})
                    # {'$push': {'specific_tweet_id': spec_tweet_id}})
                else:
                    #create query (inserting the document to that collection)
                    collectionName.insert_one({"specific_tweet_id": spec_tweet_id})
            else:
                c = c - 1
    if alltheuserslist_flag_exists:
        # update query (updating the existing document to that collection)
        for i in allthe_users.keys():
            name='all_the_users_list.'+str(i)
            collectionName.update_one({'all_the_users_list': {"$exists": True}},
                                      # {'$push': {'all_the_users_list': allthe_users}})
                                      {'$set': {name: allthe_users.get(str(i))}})
    else:
        # create query (inserting the document to that collection)
        collectionName.insert_one({"all_the_users_list": allthe_users})


def graph_generation(stop):
    # for each tweet add the user id as a node
    G = nx.Graph()
    collection = db["users_info"]
    cursor = collection.find({"all_the_users_list":{ "$exists": True}})
    for doc in cursor:
        all_the_users=doc["all_the_users_list"]
        print type(all_the_users)
        print all_the_users
        a=all_the_users["0"]
        print "a"
        print type(a)
        print a["friends"]
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


# G = nx.Graph()
# G.add_nodes_from([1,2, 3,4])
# G.add_edge(1, 2)
# options = {'node_color': 'black','node_size': 100,'width': 3}
# G=nx.dodecahedral_graph()
# plt.subplot(121)
# shells = [[2, 3, 4, 5, 6], [8, 1, 0, 19, 18, 17, 16, 15, 14, 7], [9, 10, 11, 12, 13]]
# nx.draw_shell(G, nlist=shells, **options)
# plt.show()

def emailThis(to, subject="", body="", files=[]):
    try:
        fro = "ykatsadas@gmail.com"
        import smtplib
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEBase import MIMEBase
        from email.MIMEText import MIMEText
        from email.Utils import COMMASPACE, formatdate
        from email import Encoders
        msg = MIMEMultipart()
        msg['From'] = fro
        msg['To'] = to
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        msg.attach(MIMEText(body))
        for file in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(file, "rb").read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
            msg.attach(part)
        smtp = smtplib.SMTP("smtp.gmail.com",587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(fro,sys.argv[5])#remove for git
        smtp.sendmail(fro, to, msg.as_string())
        smtp.close()
        return True
    except:
        print("  error")
        return False

try:
    # graph_generation(90)
    extract_information_for_users(1)
    # graph_generation(1)
except:
    emailThis("johnkats5896@gmail.com",subject="Crash Report",body="Check the script")


