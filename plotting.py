from datetime import datetime, timedelta
from pymongo import MongoClient
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

#This script is used to produce the majority of the plots and figures needed

# uri = "mongodb://user:SpYZ7EMlgs@snf-795686.vm.okeanos.grnet.gr:25"
# client = MongoClient(uri)
client = MongoClient('localhost', 27017)
fake = 'getMostRetweetedFake'
real = 'getMostRetweeted3'
db = client[fake]
mins = 15  # number of minutes for the time interval
savefiletype=".png"


def plot_single_graph(arr, type, show, temp,filename):
    # plot
    arr = arr[:500]  # trimming the list
    avg_np = np.array(arr)
    hndl, = plt.plot(avg_np, '-', label=type)
    plt.xlabel('Time (Sequence of {} mins intervals)'.format(mins))
    plt.ylabel('Average # of retweets')
    plt.ylim(0, 10)
    plt.xlim(0, 200)
    title = "Average propagation of {} news in Twitter"
    plt.title(title.format(type))
    if not show:
        return hndl
    plt.legend(handles=[hndl, temp])
    if show:
        plt.savefig(filename.format(mins)+savefiletype)
        plt.show()

def plot_single_boxplot_graph(data, type,filename):
    fig,ax = plt.subplots()
    plt.xlabel('Time(sequence of {} mins intervals)'.format(mins))
    plt.ylabel('Number of retweets')
    plt.ylim(0, 100)
    # plt.xlim(0, 750)
    title = "Propagation of {} news in Twitter"
    filename=filename.format(mins)+"_"+type
    plt.title(title.format(type))
    ax.boxplot(data)
    plt.savefig(filename+savefiletype)
    plt.show()

#operation 1= fills the corresponding arrays : "arr1" with number of tweets involved in this time interval (position of the array), "values" with total retweets in this time interval (position of the array) ex. first 30 mins
#operation 2=
#operation 3= returns the max number of time intervals that need to be proccessed
#operation 4=
#operation 5= set the "values" array as a 2D array : rows= tweet1, tweet 2 etc. | coloumns=1st time interval, 2nd time interval etc.
def extract_information(arr1, values, stop, operation):
    if operation == 3:
        max_timeUnits = 0
    c = 0
    for og_tweet_collection in db.collection_names():  # for every tweet
        c = c + 1
        if c > stop:
            break
        collection = db[og_tweet_collection]
        if og_tweet_collection != "users_info":
            cursor = collection.find({})  # Gets the tweets in that topic
            retweet_time = []
            # get all the retweets
            for document in cursor:
                s = document["created_at"]
                dt = datetime.now()
                dt = dt.strptime(s, '%a %b %d %H:%M:%S +0000 %Y')
                retweet_time.append(dt)  # add the time of the retweet to an array
            if len(retweet_time) != 0 and len(retweet_time)<=500:  # if the tweet had retweets or if the tweet had less than 500 retweets (keeping only under 500 retweets)
                retweet_time = sorted(retweet_time)  # sort chronologically
                # get the number of time intervals (of 30 minutes)
                start_date = retweet_time[0]
                end_date = retweet_time[-1]
                c_time = start_date
                x = []
                it = 0
                while (c_time <= end_date):
                    c_time = start_date + timedelta(minutes=mins * it)
                    x.append(c_time)  # store the start of every time interval in x array
                    it = it + 1
                #
                if operation == 3:
                    if max_timeUnits < len(x):  # initialization-get the biggest number of time intervals
                        print max_timeUnits, "cahnged to ", len(x)
                        max_timeUnits = len(x)
                elif operation == 4:
                    values.append(len(retweet_time))
                else:
                    # initialization
                    s = x[0]
                    e = x[1]
                    pointer = 0
                    v = []
                    for i in x:
                        v.append(0)
                    # fill v array with the number of retweets happened in a specific time interval
                    for i in retweet_time:
                        if i > e:
                            flag = True
                            while flag:
                                pointer = pointer + 1
                                if pointer > len(x) - 1:
                                    break
                                s = x[pointer]
                                e = x[pointer + 1]
                                if e >= i >= s:
                                    flag = False
                        if e >= i >= s:
                            v[pointer] = v[pointer] + 1
                    if operation == 1:
                        operation_one(values, arr1, v)
                    elif operation==2:
                        operation_two(v, retweet_time, arr1, c, og_tweet_collection)
                    elif operation==5:
                        twoDarrayForOperationFive.append(v)
            else:
                c = c - 1
    if operation == 3:
        return max_timeUnits

def operation_one(values, numOftweets, v):
    # Now we know how many retweets happened each 30 minutes (in v array)
    counter = 0
    for i in v:  # add the avg frequency of the tweet in the corresponding 30 minutes
        # values[counter]=values[counter]+i/float(len(retweet_time)) #<--for frequency of tweets
        values[counter] = values[counter] + i  # <--for getting the avg number of tweets
        numOftweets[counter] = numOftweets[counter] + 1  # keep track of how many tweets's retweets are in that position
        counter = counter + 1

#for multiple plots in one figure
def operation_two(values, retweet_time, axarr, c, og_tweet_collection):
    counter = 0
    for i in values:
        values[counter] = i / float(len(retweet_time))
        counter = counter + 1
    # dates = matplotlib.dates.date2num(x)
    if c <= 5:
        k = 0
        l = c - 1
    else:
        k = 1
        l = c - 6
    # axarr[k, l].plot_date(dates, values, 'r--')
    # trim the list to a smaller time interval
    if (len(values) > 30):
        values = values[:30]
    axarr[k, l].plot(values, 'r')
    axarr[k, l].set_title(og_tweet_collection)
    axarr[k, l].legend(loc="upper right", title="Total number of retwets: " + str(len(retweet_time)))
    # plt.subplot(2, 5, c)
    # plt.xticks(rotation=30)
    # plt.ylabel('Frequency of retweets')
    # plt.title(str(c))#tweet ID
    # plt.plot_date(dates, values, 'r--')
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.1, hspace=0.2)

def overall_figure(type, show, temp):
    # get the max_timeUnits number of a tweet propagation time (in 30 mins units)
    print "Calc max_timeUnits"
    max_timeUnits = extract_information([], [], 250, 3)  # it will return the maximum number of time units needed
    # initialization-create two lists values and numberOftweets and init them
    values = []
    numOftweets = []
    for x in range(0, max_timeUnits):
        values.append(0)  # on each row it has the sum of the number of retweets in the (rowNum) half-hour
        numOftweets.append(
            0)  # on each row has the number of tweets participated in values in order to calculate the avg

    extract_information(numOftweets, values, 250,
                        1)  # it will run the appropriate operations (operation_one()) in order to return the arrays numOftweets and values
    # calculate average "" of tweets in that time interval
    avg = []
    counter = 0
    for i in values:
        if numOftweets[counter] != 0:
            avg.append(i / float(numOftweets[counter]))
        else:
            avg.append(0)
        counter = counter + 1
    if show:
        plot_single_graph(avg, type, show, temp,filename='single_graph_overall_{}mins')
    else:
        return plot_single_graph(avg, type, show, [],filename='single_graph_overall_{}mins')

def overall_boxplot_figure(type):
    # get the max_timeUnits number of a tweet propagation time (in 30 mins units)
    print "Calc max_timeUnits"
    max_timeUnits = extract_information([], [], 250, 3)  # it will return the maximum number of time units needed
    # initialization-create two lists values and numberOftweets and init them
    values = []
    numOftweets = []
    for x in range(0, max_timeUnits):
        values.append(0)  # on each row it has the sum of the number of retweets in the (rowNum) half-hour
        numOftweets.append(0)  # on each row has the number of tweets participated in values in order to calculate the avg
    extract_information(numOftweets, values, 250,5)
    #Make the twoDarrayForOperationFive in a n x n form (by trimming or completing)
    max=10# max number of time intervals depicted (max num of boxplots for each period of time)
    counter=0
    for i in twoDarrayForOperationFive:
        dif = max - len(i)
        if dif>0:#completing
            a=i
            for x in range(dif):
                a.append(0)
            twoDarrayForOperationFive[counter]=a
        elif dif<0:#trimming
            a=i[:10]
            for x in range(dif):
                a.append(0)
            twoDarrayForOperationFive[counter]=a
        counter=counter+1
    formatedData=zip(*twoDarrayForOperationFive) #transpose the array for the boxplot
    plot_single_boxplot_graph(formatedData, type,filename='single_boxplot_graph_overall_{}mins')

def initialize_group_plot(rows, columns):
    f, axarr = plt.subplots(rows, columns, sharex=True, sharey=True, figsize=(20, 8))
    matplotlib.rcParams.update({'font.size': 5})
    return f, axarr

def show_group_plot(f, axarr, type,filename,verifiedUsers):
    for ax in axarr.flat:
        ax.set(xlabel='# of {} mins'.format(mins), ylabel='Percentage of retweets')
        ax.label_outer()
    for ax in f.axes:
        matplotlib.pyplot.sca(ax)
        plt.xticks(rotation=30)
    if verifiedUsers:
        title = "Propagation of {} news tweets on verified users"
    else:
        title = "Propagation of {} news tweets"
    plt.suptitle(title.format(type))
    plt.savefig(filename+'_'+type + savefiletype)
    plt.show()

def individual_fugures(type):
    f, axarr = initialize_group_plot(2, 5)
    extract_information(axarr, [], 10, 2)
    show_group_plot(f, axarr, type,filename="individual_figures_{}mins".format(mins),verifiedUsers=False)

def graphs_of_verified_users(type):
    f, axarr = initialize_group_plot(2, 5)
    ##################
    c = 0
    for og_tweet_collection in db.collection_names():  # for every tweet
        collection = db[og_tweet_collection]
        if og_tweet_collection!="users_info":
            cursor = collection.find({})  # Gets the tweets in that topic
            retweet_time = []
            flag = False
            for document in cursor:
                # if this retweet is from a verified user print YES
                if document["user"]["verified"]:
                    print document["user"]["verified"], "----", og_tweet_collection, "----", document["user"]["id"]
                    flag = True
                    s = document["created_at"]
                    dt = datetime.now()
                    dt = dt.strptime(s, '%a %b %d %H:%M:%S +0000 %Y')
                    retweet_time.append(dt)
            if flag:
                c = c + 1
                print c
                if c > 10:
                    break
                # make a graph for this tweet
                if len(retweet_time) != 0:
                    retweet_time = sorted(retweet_time)
                    start_date = retweet_time[0]
                    end_date = retweet_time[-1]
                    c_time = start_date
                    x = []
                    it = 0
                    while (c_time <= end_date):
                        c_time = start_date + timedelta(minutes=mins * it)
                        x.append(c_time)
                        it = it + 1
                    s = x[0]
                    e = x[1]
                    pointer = 0
                    values = []
                    for i in x:
                        values.append(0)
                    for i in retweet_time:
                        if i > e:
                            flag = True
                            while flag:
                                pointer = pointer + 1
                                if pointer > len(x) - 1:
                                    break
                                s = x[pointer]
                                e = x[pointer + 1]
                                if e >= i >= s:
                                    flag = False
                        if e >= i >= s:
                            values[pointer] = values[pointer] + 1
                    operation_two(values, retweet_time, axarr, c, og_tweet_collection)
                else:
                    c = c - 1
    #################
    show_group_plot(f, axarr, type,filename='individual_figures_verified_users_{}mins'.format(mins),verifiedUsers=True)

def cdf(type, show, temp):
    ratios = []  # make an array of # of retweets/# of 30 minutes
    extract_information([], ratios, 250, 4)  # operation 4(not yet implemented)
    # ratios=ratios[:40]
    # Prints the CDF diagram
    hist, bin_edges = np.histogram(ratios, normed=True)
    cdf = np.cumsum(hist)
    hndl, = plt.plot(bin_edges[1:], cdf / cdf[-1], marker='.', label=type)
    title = "Cumulative Distribution Function of {} news".format(type)
    title = "Cumulative Distribution Function of fake/real news"
    plt.xlabel('# of retweets')
    plt.ylabel('Percent')
    plt.ylim(0.6, 1.1)
    # plt.xlim(0, 750)
    plt.title(title)
    if not show:
        return hndl
    plt.legend(handles=[hndl, temp])
    if show:
        plt.savefig('cdf'+ savefiletype)
        plt.show()

def friend_follower_ratio(typeNews, show, temp):
    ratios = []  # make an array of # of retweets/# of 30 minutes
    max=0
    min=float("inf")
    #fill the array
    for og_tweet_collection in db.collection_names():
        if og_tweet_collection != "users_info":  # to avoid examining the users_info collection
            collection = db[og_tweet_collection]
            cursor = collection.find({})  # Gets the tweets in that topic
            if cursor.count()<=500:
                for document in cursor:
                    fr = float(document["user"]["friends_count"])
                    fo = float(document["user"]["followers_count"])
                    # print fr,fo
                    if fo!=0:
                        rat=float(fr/fo)
                        ratios.append(rat)
                        if rat<min:
                            min=rat
                        if rat>max:
                            max=rat
                    else:
                        ratios.append(1)
    norm_ratios=[]
    for i in ratios:
        norm_ratios.append((i-min)/(max-min))
    norm_ratios.sort(reverse=True)
    ratios_np = np.array(norm_ratios)
    hndl, = plt.plot(ratios_np, '-', label=typeNews)
    title = "Friends/Followers Ratio of fake/real news users"
    plt.xlabel('user')
    plt.ylabel('Ratio')
    plt.ylim(0, 0.05)
    plt.xlim(0, 3000)
    plt.title(title)
    if not show:
        return hndl
    plt.legend(handles=[hndl, temp])
    if show:
        plt.savefig('friends_followers_ratio_'+typeNews + savefiletype)
        plt.show()

def completion_DB_processing(type,comparisson_set):
    totalNumOfTweetChains=0
    if type=="Fake":
        totalNumOfTweetChains=90
    elif type=="Real":
        totalNumOfTweetChains=250
    #first we initialize the user_set with the id of all the user's that have been processed
    user_set = set()
    for og_tweet_collection in db.collection_names():  # initialize the all_users set, to avoid examining users that have already been examined
        if og_tweet_collection == "users_info":
            collection = db[og_tweet_collection]
            cursor = collection.find({"all_the_users_list": {"$exists": True}})
            for doc in cursor:
                dict = doc["all_the_users_list"]
                for key in dict.keys():
                    userDict=dict[key]
                    if bool(userDict):
                        user_set.add(str(key))

    print len(user_set),"users have been either entirely or partially examined in "+type+" news"
    if type == "Fake":
        comparisson_set=user_set
    arr = []
    for og_tweet_collection in db.collection_names():
        if og_tweet_collection != "users_info":  # to avoid examining the users_info collection
            collection = db[og_tweet_collection]
            cursor = collection.find({})  # Gets the tweets in that topic
            totalUsersInDoc = 0
            hasBeenExamined = 0
            for document in cursor:#for every tweet that was made for this topic
                totalUsersInDoc = totalUsersInDoc + 1
                if user_set.__contains__(document["user"]["id_str"]):
                    hasBeenExamined = hasBeenExamined + 1
            #add the completion percentage of this tweet chain
            if totalUsersInDoc != 0:
                arr.append(float(float(hasBeenExamined) / float(totalUsersInDoc)))
                # print "pairs",hasBeenExamined,totalUsersInDoc
                # print "div",float(float(hasBeenExamined)/float(totalUsersInDoc))
            else:
                arr.append(-0.1)
    #print percentages
    gr_than_zero = 0
    above_a_percentage = 0
    percentage = 0.8
    for i in arr:
        if i > 0:
            gr_than_zero = gr_than_zero + 1
        if i > percentage:
            above_a_percentage = above_a_percentage + 1
    print gr_than_zero, " / "+str(totalNumOfTweetChains)
    print above_a_percentage, " / "+str(totalNumOfTweetChains)
    arr.sort(reverse=True)
    arr_np = np.array(arr)
    plt.axhline(y=0, color='crimson')
    hndl, = plt.plot(arr_np, '-', label=type)
    plt.xlabel('news(tweet chains)')
    plt.ylabel('percentage of completion')
    title="For how many {} news has the script finished"
    plt.title(title.format(type))
    # plt.legend(handles=[hndl, temp])
    title="completion_stats_"+type
    plt.savefig(title+savefiletype)
    plt.show()

    print len(comparisson_set), "comparisson_set length"
    print len(user_set), "user_set length"
    # see how many users the two sets (fake/real) have in common
    if type == "Real":
        c=0
        for i in user_set:
            if comparisson_set.__contains__(i):
                c=c+1
        print "Users in common", c
    else:
        return comparisson_set

# #~~~~~~~~~~~~~Overall~~~~~~~~~~~~~ 1 figure
# db = client[fake]
# temp=overall_figure("Fake",False,[])
# db = client[real]
# overall_figure("Real",True,temp)
# #~~~~~~~~~~~~~Overall with Boxplots~~~~~~~~~~~~~ 2 figures
twoDarrayForOperationFive=[] #leave this out of the comments - it might cause errors
# db = client[fake]
# overall_boxplot_figure("Fake")
# twoDarrayForOperationFive=[]
# db = client[real]
# overall_boxplot_figure("Real")
# #~~~~~~~~~~~~~Individual~~~~~~~~~~~~~ 2 figures
# db = client[fake]
# individual_fugures("Fake")
# db = client[real]
# individual_fugures("Real")
# #~~~~~~~~~~~~~Verified Users~~~~~~~~~~~~~ 2 figures
# db = client[fake]
# graphs_of_verified_users("Fake")
# db = client[real]
# graphs_of_verified_users("Real")
# #~~~~~~~~~~~~CDF~~~~~~~~~~~~~~ 1 figure
# db = client[fake]
# temp = cdf("fake", False, [])
# db = client[real]
# cdf("real", True, temp)
# #~~~~~~~~~~~~Friends/Followers Ratio~~~~~~~~~~~~~~ 1 figure
# db = client[fake]
# temp = friend_follower_ratio("fake", False, [])
# db = client[real]
# friend_follower_ratio("real", True, temp)
# #~~~~~~~~~~~~Completion of DB processing~~~~~~~~~~~~~~ 2 figures
comparisson_set=set()
db = client[fake]
comparisson_set=completion_DB_processing("Fake",comparisson_set)
db = client[real]
completion_DB_processing("Real",comparisson_set)
