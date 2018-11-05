import networkx as nx
from pymongo import MongoClient
import sys
import tweepy
import matplotlib.pyplot as plt

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

# def graph_generation(stop):
#     # for each tweet add the user id as a node
#     G = nx.Graph()
#     collection = db["users_info"]
#     cursor = collection.find({"all_the_users_list": {"$exists": True}})
#     # for doc in cursor:
#     #     all_the_users=doc["all_the_users_list"]
#     #     print type(all_the_users)
#     #     print all_the_users
#     #     a=all_the_users["0"]
#     #     print "a"
#     #     print type(a)
#     #     print a["friends"]
#     # c = 0
#     # for og_tweet_collection in db.collection_names():  # for every tweet
#     #     c = c + 1
#     #     if c > stop:
#     #         break
#     #     collection = db[og_tweet_collection]
#     #     cursor = collection.find({})  # Gets the tweets in that topic
#     #     user_connections = []
#     #     tweet = api.get_status(og_tweet_collection)
#     #     user_connections.append(tweet.user.id)
#     #     # get all the retweets
#     #     for document in cursor:
#     #         id = document["user"]["id"]
#     #         user_connections.append(id)
#     #     if len(user_connections) > 1:  # if the tweet had retweets
#     #         G.add_nodes_from(user_connections)  # set people who retweeted this as nodes
#     #         i = 0
#     #         for k in user_connections:
#     #             if i != 0:  # if it is not the original poster
#     #                 # TO DO: get the inf from the DB
#     #                 G.add_edge(user_connections[0], k)  # add it as a node
#     #                 for j in user_connections:
#     #                     if k != j:
#     #                         if j in user_followers or j in user_friends:
#     #                             G.add_edge(j, k)  # if there is a connection between friends/followers add the edge
#     #             i = i + 1
#     #         nx.draw(G)
#     #         plt.show()
#     #     else:
#     #         c = c - 1


def graph_generation(stop):
    # for each tweet add the user id as a node
    G = nx.Graph()
    collection = db["users_info"]
    cursor = collection.find({"all_the_users_list": {"$exists": True}})
    userList=[]
    friendsUsersList=[]
    followersUsersList = []
    counter=0
    # for every user who exists here add him as a node to the graph
    for doc in cursor:
        all_the_users=doc["all_the_users_list"]
        for user in all_the_users:
            if all_the_users[user] is not None:
                if counter<=stop:
                    G.add_node(user)
                    userList.append(user)
                    followers_of_the_user=all_the_users[user]["followers"]
                    friends_of_the_user = all_the_users[user]["friends"]
                    print user, len(followers_of_the_user),len(friends_of_the_user)
                    for friend in friends_of_the_user:
                        G.add_node(friend)
                        G.add_edge(user, friend)
                        friendsUsersList.append(friend)
                    for follower in followers_of_the_user:
                        G.add_node(follower)
                        G.add_edge(user, follower)
                        followersUsersList.append(follower)
                counter=counter+1
    # generate positions for the nodes
    print"drawing"
    pos = nx.random_layout(G)  # positions for all nodes
    nx.draw_networkx_nodes(G, pos,nodelist=userList,node_color='r',node_size=10,alpha=0.8)
    nx.draw_networkx_nodes(G, pos,nodelist=friendsUsersList,node_color='b',node_size=0.001,alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=0.01, alpha=0.5,edge_color='g')
    plt.show()

def graph_generation_basedOn_tweet(stop):
    # for each tweet add the user id as a node
    collection = db["users_info"]
    all_the_users={}

    cursor = collection.find({"all_the_users_list": {"$exists": True}})
    # for every user who exists here add it as a node to the graph
    for doc in cursor:
        all_the_users.update(doc["all_the_users_list"])

    cursor = collection.find({"specific_tweet_id": {"$exists": True}})
    for doc in cursor:
        G = nx.Graph()
        dic=doc["specific_tweet_id"]
        for tweet in dic:
            flag=False
            nodes = []
            emptyNodes=[]
            for tweetKey in tweet.keys():
                status = api.get_status(id=tweetKey)
                source = status.user.id
                sourceName=status.user.screen_name
                usersInvolvedList=tweet[tweetKey]
                for user in usersInvolvedList:
                    G.add_node(user)
                    nodes.append(user)
                for user in usersInvolvedList:
                    for otherUser in usersInvolvedList:
                        if user is not otherUser:
                            oU=all_the_users.get(str(otherUser))
                            if oU is not None:
                                flag=True
                                if user in oU["followers"]:
                                    print "foll",user,otherUser
                                    G.add_edge(user, otherUser)
                                if user in oU["friends"]:
                                    print "frie",user,otherUser
                                    G.add_edge(user, otherUser)
                            else:
                                emptyNodes.append(otherUser)

            if flag:
                # generate positions for the nodes
                print"drawing"
                print sourceName,len(G.nodes)
                nx.write_edgelist(G, "TweetGraph_{}.csv".format(str(sourceName)), data=False)
                pos = nx.random_layout(G)  # positions for all nodes
                nx.draw_networkx_nodes(G, pos,nodelist=nodes,node_color='r',node_size=10,alpha=0.8)
                nx.draw_networkx_nodes(G, pos,nodelist=[source],node_color='b',node_size=50,alpha=0.8)
                nx.draw_networkx_nodes(G, pos, nodelist=emptyNodes, node_color='black', node_size=5, alpha=0.8)
                nx.draw_networkx_edges(G, pos, width=1, alpha=0.5,edge_color='g')
                plt.title(tweetKey+" from "+sourceName)
                plt.show()



def graph_generation_basedOn_tweet_with_hops1(stop):
    # for each tweet add the user id as a node
    collection = db["users_info"]
    all_the_users = {}

    cursor = collection.find({"all_the_users_list": {"$exists": True}})
    # for every user who exists here add it as a node to the graph
    for doc in cursor:
        all_the_users.update(doc["all_the_users_list"])

    cursor = collection.find({"specific_tweet_id": {"$exists": True}})
    for doc in cursor:
        G = nx.Graph()
        dic = doc["specific_tweet_id"]
        for tweet in dic:
            flag = False
            nodes = []
            emptyNodes = []
            for tweetKey in tweet.keys():
                status = api.get_status(id=tweetKey)
                source = status.user.id
                sourceName = status.user.screen_name
                usersInvolvedList = tweet[tweetKey]
                for user in usersInvolvedList:
                    G.add_node(user)
                    nodes.append(user)
                for user in usersInvolvedList:
                    for otherUser in usersInvolvedList:
                        if user is not otherUser:
                            oU = all_the_users.get(str(otherUser))
                            if oU is not None:
                                flag = True
                                if user in oU["followers"]:
                                    print "foll", user, otherUser
                                    G.add_edge(user, otherUser)
                                if user in oU["friends"]:
                                    print "frie", user, otherUser
                                    G.add_edge(user, otherUser)
                            else:
                                emptyNodes.append(otherUser)





            # nodesEntered=[]
            # edgesEntered={}
            # distanceDict={}
            # sortedReference=[]
            # #make the distance dictionary node:path,distance
            # i=0
            # for user in G.nodes():
            #     shortestPath=nx.shortest_path(G,user,source)
            #     length=len(shortestPath)-1
            #     distanceDict[user]=shortestPath
            #     #add this node to the correct position on the reference list
            #     if(i==0):
            #         sortedReference.append([user,length])
            #     else:
            #         j=0
            #         isNotPlaced=True
            #         for anotherNode in sortedReference:
            #            if anotherNode[1]<length and isNotPlaced:
            #                #add this node to the specific position
            #                b = sortedReference[:]
            #                b[j:j] = [[user,length]]
            #                sortedReference=b
            #                isNotPlaced=False
            #            j=j+1
            #         # if the node hasn't been added and we've reached the end add it in the end
            #         if isNotPlaced:
            #             sortedReference.append([user,length])
            #     i=i+1
            #
            # #for every node of the dictionary, from bigger distance to smaller
            # for node in sortedReference:
            #     path=distanceDict.get(node)
            #     for user in path:
            #         #add the user as a node if they dont already exist in the graph
            #     x=0
            #     for user in path:
            #         #add the edge of the user with the next one if they are not already connected
            #         connections=edgesEntered.get(user)
            #         if x+1!=len(path):
            #             if path[x+1] in connections:
            #
            #
            #         x=x+1
            # #add the path and the missing edges and nodes to the new graph


            if flag:
                # generate positions for the nodes
                print"drawing"
                nx.write_edgelist(G, "TweetGraph_{}.csv".format(str(sourceName)), data=False)
                pos = nx.random_layout(G)  # positions for all nodes
                nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color='r', node_size=10, alpha=0.8)
                nx.draw_networkx_nodes(G, pos, nodelist=[source], node_color='b', node_size=50, alpha=0.8)
                nx.draw_networkx_nodes(G, pos, nodelist=emptyNodes, node_color='black', node_size=5, alpha=0.8)
                nx.draw_networkx_edges(G, pos, width=1, alpha=0.5, edge_color='g')
                plt.title(tweetKey + " from " + sourceName)
                plt.show()


def graph_generation_basedOn_tweet_with_hops(stop):
    # fill all_the_users with all the users and their relations that there are
    collection = db["users_info"]
    all_the_users = {}
    cursor = collection.find({"all_the_users_list": {"$exists": True}})
    for doc in cursor:
        all_the_users.update(doc["all_the_users_list"])

    cursor = collection.find({"specific_tweet_id": {"$exists": True}})
    p = 0
    for doc in cursor:
        G = nx.Graph()
        dic = doc["specific_tweet_id"]
        for tweet in dic:
            flag = False
            for tweetKey in tweet.keys():
                status = api.get_status(id=tweetKey)
                source = status.user.id
                sourceName = status.user.screen_name
                usersInvolvedList = tweet[tweetKey]
                #make the userSet
                userSet=set()
                for user in usersInvolvedList:
                    userSet.add(user)
                level=[source]
                G.add_node(source)
                userSet.remove(source)
                while(len(level)!=0):
                    newLevel=[]
                    for user in level:
                        toBeDeleted=[]
                        for anotherUser in userSet:
                            aU = all_the_users.get(str(anotherUser))
                            if aU is not None:
                                flag = True
                                if user in aU["followers"] or user in aU["friends"]:
                                    newLevel.append(anotherUser)
                                    toBeDeleted.append(anotherUser)
                                    G.add_node(anotherUser)
                                    G.add_edge(user, anotherUser)
                        for user in toBeDeleted:
                            userSet.remove(user)
                    level=newLevel
                #add the users that are left as rogue nodes
                for user in userSet:
                    G.add_node(user)
            if flag:
                print "exporting"
                print sourceName,len(G.nodes)
                nx.write_edgelist(G, "TweetGraph_{}.csv".format(str(sourceName)+str(p)), data=False)
            p=p+1








#--------------------EXECUTION----------------------
#______________Network of a single tweet____________
db = client[fake]
graph_generation_basedOn_tweet(0)
db = client[real]
graph_generation_basedOn_tweet(0)
#___________________________________________________
#________Network of a single tweet with hops________
db = client[fake]
graph_generation_basedOn_tweet_with_hops(0)
db = client[real]
graph_generation_basedOn_tweet_with_hops(0)
#___________________________________________________
#---------------------------------------------------