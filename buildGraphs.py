import networkx as nx
from pymongo import MongoClient
import sys
import tweepy
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join

client = MongoClient('localhost', 27017)
fake = 'getMostRetweetedFakeFinalFebruary'
real = 'getMostRetweetedRealFinalFebruary'
db = client[fake]
fake_accounts=[1266239359,2302467404,2455959913,4730093353,17793358,735574058167734273,393693452,2371044266,525815006,375721095,457984599,141422795,828075242597785600,168541923,183036873,1121890495,18118505,4081106480,20708260,69666298,34927577,2217181338,39308549,20818801,2361224263,14669951,455764741,187578616,948197130782629888,19985444,559802746,50434933,18927538,3016071993,18856867,15843059,15115280,15669672,14792049,18643437,850036892,16041234,2467720274,19211550,134360868,3092154496,707278892801765377,469194846]
real_accounts=[428333,759251,2097571,1652541,335455570,15108702,5402612,742143,612473,5988062,32353291,32357365,34713362,104237736,144274618,807095,1877831,3108351,23484039,16311797,14345062,2467791,51241574,49304503,14677919]

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
                nx.write_edgelist(G, "graphs/TweetGraph_{}.csv".format(str(sourceName)+"_"+str(tweetKey)), data=False)
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


def graph_generation_basedOn_tweet_with_hops(stop,type):
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
                try:
                    status = api.get_status(id=tweetKey)
                    source = status.user.id
                    sourceName = status.user.screen_name
                except:
                    source=0
                    sourceName="deleted"
                usersInvolvedList = tweet[tweetKey]
                #make the userSet
                userSet=set()
                for user in usersInvolvedList:
                    userSet.add(user)
                level=[source]
                G.add_node(source)
                if source!=0:
                    userSet.remove(source)
                else:
                    if 183036873 in userSet:
                        userSet.remove(183036873)
                    elif 2302467404 in userSet:
                        userSet.remove(2302467404)
                    elif 4730093353 in userSet:
                        userSet.remove(4730093353)
                    elif 375721095 in userSet:
                        userSet.remove(375721095)
                    elif 707278892801765377 in userSet:
                        userSet.remove(707278892801765377)
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
                    #---------here we add all the single nodes to an imaginary node called -1 so that we can delete it in gephi later on
                    node_list=list(G.nodes)
                    for node in node_list:
                        neighbors_list=[n for n in G.neighbors(node)]
                        if len(neighbors_list)==0:
                            G.add_edge(node, -1)
                    #-----------------------------
                    print "exporting"
                    print sourceName,len(G.nodes)
                    typepath=""
                    if type is "Fake":
                        typepath="fake/"
                    else:
                        typepath="real/"
                    nx.write_edgelist(G, "graphs/"+typepath+"TweetGraph_{}.csv".format(str(sourceName)+"_"+str(tweetKey)), data=False)
                p=p+1


#The following fuction will take as long as it would take to collect the data and build the graphs later
def graph_generation_basedOn_tweet_with_friendship(stop):
    for og_tweet_collection in db.collection_names():#for every tweet
        tweet_users=[]
        G = nx.Graph()
        if og_tweet_collection != "users_info":  # to avoid examining the users_info collection
            #get the original tweet and save the source on a set to count it
            try:
                tweet= api.get_status(id=og_tweet_collection)
                user_id=tweet.user.id_str
            except:
               print ("----suspended user----")
               user_id=0
            # create node of the source
            tweet_users.append(user_id)
            G.add_node(user_id)
            collection=db[og_tweet_collection]
            cursor = collection.find({})
            for doc in cursor:# for every retweet
                userId=int(doc["user"]["id"])
                # create node of the retweeter
                tweet_users.append(userId)
                G.add_node(userId)
            for node in tweet_users:#for every node
                for otherNode in tweet_users:
                    if node!=otherNode:#check every other node for friendship
                        status = api.show_friendship(source_id=node, target_id=otherNode)
                        if status[0].following or status[1].following:
                            G.add_edge(node,otherNode)

            # generate positions for the nodes
            nx.write_edgelist(G, "graphs/TweetGraph_{}.csv".format(str(user_id)+"_"+str(og_tweet_collection)), data=False)



def get_four_split(char,dic):
    nodes=[]
    if char is not 'degree':
        for n in dic:
            nodes.append((n.encode("utf-8"), dic[n]))
    else:
        nodes=dic
    low=[]
    mid=[]
    high=[]
    low_num=0
    mid_num=0
    high_num=0
    sortednodes=sorted(nodes, key=lambda tup: tup[1])
    num=len(nodes)/4
    i=0
    for n in sortednodes:
        if i<num:
            low.append(n)
            low_num=n[1]
        elif i>=num and i<(num*3):
            if n[1]==low_num:
                low.append(n)
            else:
                mid.append(n)
                mid_num=n[1]
        elif i>=(num*3):
            if n[1] == mid_num:
                mid.append(n)
            elif n[1]==low_num:
                low.append(n)
            else:
                high.append(n)
            high_num=n[1]
        i=i+1

    if len(high)==0:
        high=mid
        mid=[]
    if char is 'degree':
        print low
    return low,mid,high

def get_a_list_of_the_first_of_a_tuple(t_list):
    just_a_list=[]
    for t in t_list:
        just_a_list.append(t[0])
    return just_a_list

#reads a graph and classifies the nodes
def read_a_graph(path):
    print path
    type=str(path[-4:])
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    # print onlyfiles
    all_graphs={}
    for f in onlyfiles:
        G = nx.read_edgelist(path+'/'+f,delimiter=" ")
        print "---------"+f+"----------"
        print "BEFORE"
        print "nodes:",len(G)
        print "edges:",G.number_of_edges()
        if G.has_node('-1'):
            G.remove_node('-1')
        print "AFTER"
        print "nodes:", len(G)
        print "edges:", G.number_of_edges()
        if G.number_of_edges()>=(len(G)/4):
            print "TAKE THIS ONE: ","-",type,"-",f
        ###########CHECK HOW MANY ACCOUNTS OF OUR LIST IS IN THE TWEET CHAIN##########
        involved=[]
        if type== "fake":
            accounts = fake_accounts
        else:
            accounts = real_accounts
        for node in G.nodes():
            if int(node) in accounts:
                involved.append(int(node))
        print "INVOLVED USERS:",len(involved)
        print involved
        #######################################################
        density= nx.density(G)
        degree=nx.degree(G)
        bc= nx.betweenness_centrality(G)
        cc= nx.closeness_centrality(G)
        graph={"density":density,"degree":degree,"bc":bc,"cc":cc}
        all_graphs[f]=graph
        print"--------------------------"
        # plt.title(f)
        # nx.draw(G)
        # plt.show()
    # print all_graphs
    for g in all_graphs:
        print g
        cc_low=[]
        cc_mid=[]
        cc_high=[]

        bc_low=[]
        bc_mid = []
        bc_high = []

        degree_low=[]
        degree_mid = []
        degree_high = []

        list_of_nodes = []
        for n in all_graphs[g]['cc']:
            list_of_nodes.append(n.encode("utf-8"))
        # for every characteristic split in 4
        for char in all_graphs[g]:
            if char is not 'density':
                low,mid,high=get_four_split(char,all_graphs[g][char])
                if char is 'cc':
                    cc_low=low
                    cc_mid=mid
                    cc_high=high
                elif char is 'bc':
                    bc_low=low
                    bc_mid=mid
                    bc_high=high
                elif char is 'degree':
                    degree_low=low
                    degree_mid=mid
                    degree_high=high
        classified=[]
        for n in list_of_nodes:
            if n in get_a_list_of_the_first_of_a_tuple(cc_low) and n in get_a_list_of_the_first_of_a_tuple(degree_high):
                classified.append((n,"A"))
            elif n in get_a_list_of_the_first_of_a_tuple(degree_high) and n in get_a_list_of_the_first_of_a_tuple(bc_low):
                classified.append((n, "B"))
            elif n in get_a_list_of_the_first_of_a_tuple(cc_high) and n in get_a_list_of_the_first_of_a_tuple(degree_low):
                classified.append((n, "C"))
            elif n in get_a_list_of_the_first_of_a_tuple(cc_high) and n in get_a_list_of_the_first_of_a_tuple(bc_low):
                classified.append((n, "D"))
            elif n in get_a_list_of_the_first_of_a_tuple(bc_high) and n in get_a_list_of_the_first_of_a_tuple(degree_low):
                classified.append((n, "E"))
            elif n in get_a_list_of_the_first_of_a_tuple(bc_high) and n in get_a_list_of_the_first_of_a_tuple(cc_low):
                classified.append((n, "F"))
            elif n in get_a_list_of_the_first_of_a_tuple(bc_high):
                classified.append((n, "G"))
            else:
                classified.append((n, "-"))
        with open(g+".txt", "w") as text_file:
            for n in classified:
                print n
                text_file.write(str(n)+'\n')
        print "______________________________"
    counter=0
    sum=0
    for g in all_graphs:
        sum=all_graphs[g]['density']
        counter=counter+1
    avg=sum/counter
    print"average density is",avg














# read_a_graph(r"C:\Users\johnk\Desktop\thesis\remoteDevelopment\graphs")
#--------------------EXECUTION----------------------
#______________Network of a single tweet____________
# db = client[fake]
# graph_generation_basedOn_tweet(0)
# db = client[real]
# graph_generation_basedOn_tweet(0)
#___________________________________________________
#________Network of a single tweet with hops________THIS ONE WE USE
# db = client[fake]
# graph_generation_basedOn_tweet_with_hops(0,"Fake")
# db = client[real]
# graph_generation_basedOn_tweet_with_hops(0,"Real")
#___________________________________________________
#________Network of a single tweet with hops based on friendship________
# db = client[fake]
# graph_generation_basedOn_tweet_with_friendship(0)
# db = client[real]
# graph_generation_basedOn_tweet_with_friendship(0)
#___________________________________________________
#________Export metrics________THIS ONE WE USE
path=r"C:\Users\johnk\Desktop\thesis\remoteDevelopment\graphs"
print "___________FAKE_____________"
read_a_graph(path+r"\fake")
print "___________REAL_____________"
read_a_graph(path+r"\real")
#___________________________________________________
#---------------------------------------------------