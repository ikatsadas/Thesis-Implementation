from datetime import datetime, timedelta
from pymongo import MongoClient
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
from sklearn import preprocessing
import sys
import tweepy

#This script is used to produce the majority of the plots and figures needed

ACCESS_TOKEN = sys.argv[3]
ACCESS_SECRET = sys.argv[4]
CONSUMER_KEY = sys.argv[1]
CONSUMER_SECRET = sys.argv[2]
auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

api = tweepy.API(auth, retry_count=10, retry_delay=5, retry_errors=set([103]), wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

client = MongoClient('localhost', 27017)
fake = 'nameDB'
real = 'nameDB'
db = client[fake]
mins = 30  # number of minutes for the time interval
savefiletype=".svg"
dir='figures/'
subdir=' minutes/'

twoDarrayForOperationFive=[]
split_per_retweetNumber=100
retweet_limit=500  # if the tweet had retweets or if the tweet had less than 500 retweets (keeping only under 500 retweets)

#iteration_batches, on which batch we are on in this iteration, used to choose a different batch everytime from the collections (if split_per_retweetNumber is 0 then this parameter doesnt matter(default=0))
#total_iterations, used in the case we want to split our dataset in batches (default=0)
def plot_single_graph(arr, type, show,ytitle, temp,counter_of_tweets_examined,filename,iteration_batches=0,total_iterations=0,y_lim=(0,10),x_lim=(0,200)):
    # plot
    arr = arr[:500]  # trimming the list
    if ytitle=='Percentage change number of retweets' and not show:
        plt.axhline(y=0, color='crimson')#to place a red line on y=0
    avg_np = np.array(arr)
    if show:
        hndl, = plt.plot(avg_np, '-', label=type + str(" news tweets"), alpha=0.7)
    else:
        hndl, = plt.plot(avg_np, '-', label=type + str(" news tweets"))
    plt.xlabel('Time (Sequence of {} mins intervals)'.format(mins))
    plt.ylabel(ytitle)

    plt.ylim(y_lim)
    plt.xlim(x_lim)
    if total_iterations==0:#we DO NOT want to split it, we want it all
        plt.title("Average propagation of news in Twitter")
    else:#we want to split it
        lower=iteration_batches * split_per_retweetNumber
        upper=(iteration_batches + 1) * split_per_retweetNumber
        if total_iterations==iteration_batches:
            plt.title(
                "Average propagation of news in Twitter, number of retweets=[" + str(lower) + "," + str(upper) + "]")
        else:
            plt.title("Average propagation of news in Twitter, number of retweets=["+str(lower)+","+str(upper)+")")
    if not show:
        return [hndl,mpatches.Patch(color=hndl.get_color(), label='Number of '+type+' news tweets '+str(counter_of_tweets_examined))]
    plt.legend(handles=[hndl, temp[0],mpatches.Patch(color=hndl.get_color(), label='Number of '+type+' news tweets '+str(counter_of_tweets_examined)),temp[1]])
    if show:
        if total_iterations == 0:  # we DO NOT want to split it, we want it all
            plt.savefig(dir+str(mins)+subdir+filename.format(mins)+savefiletype)
        else:  # we want to split it
            plt.savefig(dir+str(mins)+subdir+filename.format(mins)+"_batchNum_"+str(iteration_batches+1) + savefiletype)
        plt.show()

def plot_single_boxplot_graph(data, type,filename,iteration_batches=0,total_iterations=0):
    fig,ax = plt.subplots()
    plt.xlabel('Time(sequence of {} mins intervals)'.format(mins))
    plt.ylabel('Number of retweets')
    plt.ylim(0, 80)
    if total_iterations == 0:  # we DO NOT want to split it, we want it all
        title = "Propagation of {} news in Twitter"
    else:#we want to split it
        lower=iteration_batches * split_per_retweetNumber
        upper=(iteration_batches + 1) * split_per_retweetNumber
        if total_iterations==iteration_batches:
            title = "Propagation of {} news in Twitter, number of retweets=[" + str(lower) + "," + str(upper) + "]"
        else:
            title = "Propagation of {} news in Twitter, number of retweets=[" + str(lower) + "," + str(upper) + ")"
    filename=filename.format(mins)+"_"+type
    plt.title(title.format(type))
    ax.boxplot(data)
    plt.xticks(rotation=45)
    if total_iterations == 0:  # we DO NOT want to split it, we want it all
        plt.savefig(dir+str(mins)+subdir+filename + savefiletype)
    else:  # we want to split it
        plt.savefig(dir+str(mins)+subdir+filename + "_batchNum_" + str(iteration_batches + 1) + savefiletype)
    plt.show()

#operation 1= fills the corresponding arrays : "arr1" with number of tweets involved in this time interval (position of the array), "values" with total retweets in this time interval (position of the array) ex. first 30 mins
#operation 3= returns the max number of time intervals that need to be proccessed
#operation 5= set the "values" array as a 2D array : rows= tweet1, tweet 2 etc. | coloumns=1st time interval, 2nd time interval etc.
#iteration_batches, on which batch we are on in this iteration, used to choose a different batch everytime from the collections (if split_per_retweetNumber is 0 then this parameter doesnt matter(default=0))
#total_iterations, used in the case we want to split our dataset in batches (default=0)
def extract_information(arr1, values, stop, operation,iteration_batches=0,total_iterations=0):
    if operation == 3:
        max_timeUnits = 0
    c = 0
    counter_of_tweets_examined=0
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
            flagg=True
            if total_iterations == 0:#if we DO NOT want to split it in to batches
                flagg = True# continue to process it, as normal
            else:#if we DO want to split it in to batches
                # continue to print the following batch
                if ((iteration_batches * split_per_retweetNumber <= len(retweet_time)) and (iteration_batches + 1) * split_per_retweetNumber > len(retweet_time)) or (total_iterations == iteration_batches and len(retweet_time) == retweet_limit):
                    flagg = True #continue
                else:#not the current batch
                    flagg = False #skip this batch
            if flagg:
                if len(retweet_time) != 0 and len(retweet_time)<=retweet_limit:  # if the tweet had retweets or if the tweet had less than 500 retweets (keeping only under 500 retweets)
                    counter_of_tweets_examined = counter_of_tweets_examined + 1
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
        return max_timeUnits,counter_of_tweets_examined

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

#iteration and num_of_iterations are used in the case we want to split our dataset in to batches (default=0)
def overall_figure(type, show, temp,iteration=0,num_of_iterations=0):
    # get the max_timeUnits number of a tweet propagation time (in 30 mins units)
    print "Calc max_timeUnits"
    if num_of_iterations==0:#we dont want to split it into batches, we want ALL of it
        max_timeUnits,counter_of_tweets_examined = extract_information([], [], 500, 3)  # it will return the maximum number of time units needed
    else:#we want to split it into batches
        max_timeUnits,counter_of_tweets_examined = extract_information([], [], 500, 3,iteration_batches=iteration,total_iterations=num_of_iterations)  # it will return the maximum number of time units needed
    # initialization-create two lists values and numberOftweets and init them
    values = []
    numOftweets = []
    for x in range(0, max_timeUnits):
        values.append(0)  # on each row it has the sum of the number of retweets in the (rowNum) half-hour
        numOftweets.append(
            0)  # on each row has the number of tweets participated in values in order to calculate the avg

    if num_of_iterations == 0:  # we dont want to split it into batches, we want ALL of it
        extract_information(numOftweets, values, 500,1)  # it will run the appropriate operations (operation_one()) in order to return the arrays numOftweets and values
    else:#we want to split it into batches
        extract_information(numOftweets, values, 500,
                            1,iteration_batches=iteration,total_iterations=num_of_iterations)  # it will run the appropriate operations (operation_one()) in order to return the arrays numOftweets and values
    # calculate average "" of tweets in that time interval
    avg = []
    counter = 0
    for i in values:
        if numOftweets[counter] != 0:
            avg.append(i / float(numOftweets[counter]))
        else:
            avg.append(0)
        counter = counter + 1
    xlim = 0
    ylim = 0
    if show:
        if num_of_iterations == 0:  # we dont want to split it into batches, we want ALL of it
            plot_single_graph(avg, type, show,'Average number of retweets', temp,counter_of_tweets_examined,filename='single_graph_overall_{}mins',y_lim=ylim,x_lim=xlim)
        else:  # we want to split it into batches
            plot_single_graph(avg, type, show,'Average number of retweets', temp,counter_of_tweets_examined, filename='single_graph_overall_{}mins', iteration_batches = iteration, total_iterations = num_of_iterations,y_lim=0,x_lim=0)
    else:
        if num_of_iterations == 0:  # we dont want to split it into batches, we want ALL of it
            return plot_single_graph(avg, type, show,'Average number of retweets', [],counter_of_tweets_examined,filename='single_graph_overall_{}mins',y_lim=ylim,x_lim=xlim)
        else:  # we want to split it into batches
            return plot_single_graph(avg, type, show,'Average number of retweets', [],counter_of_tweets_examined, filename='single_graph_overall_{}mins', iteration_batches = iteration, total_iterations = num_of_iterations,y_lim=0,x_lim=0)

def overall_boxplot_figure(type,iteration=0,num_of_iterations=0):
    # get the max_timeUnits number of a tweet propagation time (in 30 mins units)
    print "Calc max_timeUnits"
    if num_of_iterations == 0:  # we dont want to split it into batches, we want ALL of it
        max_timeUnits,counter_of_tweets_examined = extract_information([], [], 500, 3)  # it will return the maximum number of time units needed
    else:  # we want to split it into batches
        max_timeUnits,counter_of_tweets_examined = extract_information([], [], 500, 3,iteration_batches=iteration,total_iterations=num_of_iterations)  # it will return the maximum number of time units needed
    # initialization-create two lists values and numberOftweets and init them
    values = []
    numOftweets = []
    for x in range(0, max_timeUnits):
        values.append(0)  # on each row it has the sum of the number of retweets in the (rowNum) half-hour
        numOftweets.append(0)  # on each row has the number of tweets participated in values in order to calculate the avg
    if num_of_iterations == 0:  # we dont want to split it into batches, we want ALL of it
        extract_information(numOftweets, values, 500,5)
    else:  # we want to split it into batches
        extract_information(numOftweets, values, 500, 5,iteration_batches=iteration,total_iterations=num_of_iterations)
    #Make the twoDarrayForOperationFive in a n x n form (by trimming or completing)
    max=40# max number of time intervals depicted (max num of boxplots for each period of time)
    counter=0
    for i in twoDarrayForOperationFive:
        dif = max - len(i)
        if dif>0:#completing
            a=i
            for x in range(dif):
                a.append(0)
            twoDarrayForOperationFive[counter]=a
        elif dif<0:#trimming
            a=i[:40]
            for x in range(dif):
                a.append(0)
            twoDarrayForOperationFive[counter]=a
        counter=counter+1
    formatedData=zip(*twoDarrayForOperationFive) #transpose the array for the boxplot
    plot_single_boxplot_graph(formatedData, type,filename='single_boxplot_graph_overall_{}mins',iteration_batches=iteration,total_iterations=num_of_iterations)

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
    plt.savefig(dir+str(mins)+subdir+filename+'_'+type + savefiletype)
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

def cdf(type, show, temp,iteration=0,num_of_iterations=0):
    ratios = []  # make an array of # of retweets/# of 30 minutes
    if num_of_iterations == 0:  # we dont want to split it into batches, we want ALL of it
        extract_information([], ratios, 500, 4)  # operation 4(not yet implemented)
    else:  # we want to split it into batches
        extract_information([], ratios, 500, 4,iteration_batches=iteration,total_iterations=num_of_iterations)  # operation 4(not yet implemented)
    # ratios=ratios[:40]
    # Prints the CDF diagram
    hist, bin_edges = np.histogram(ratios, normed=True)
    cdf = np.cumsum(hist)
    hndl, = plt.plot(bin_edges[1:], cdf / cdf[-1], marker='.', label=type)
    if num_of_iterations == 0:  # we dont want to split it into batches, we want ALL of it
        title = "Cumulative Distribution Function of news"
    else:  # we want to split it
        lower = iteration * split_per_retweetNumber
        upper = (iteration + 1) * split_per_retweetNumber
        if num_of_iterations == iteration:
            title = "Cumulative Distribution Function of news, number of retweets=[" + str(lower) + "," + str(upper) + "]"
        else:
            title = "Cumulative Distribution Function of news, number of retweets=[" + str(lower) + "," + str(upper) + ")"

    plt.xlabel('# of retweets')
    plt.ylabel('Percent')
    # plt.ylim(0.6, 1.1)
    # plt.xlim(0, 750)
    plt.title(title)
    if not show:
        return hndl
    plt.legend(handles=[hndl, temp])
    if show:
        if num_of_iterations == 0:  # we DO NOT want to split it, we want it all
            plt.savefig(dir+'cdf' + savefiletype)
        else:  # we want to split it
            plt.savefig(dir+'cdf' +"_batchNum_"+str(iteration+1) + savefiletype)
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
        plt.savefig(dir+'friends_followers_ratio_'+typeNews + savefiletype)
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
    plt.savefig(dir+title+savefiletype)
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

def overall_percentages_change(type, show, temp,iteration=0,num_of_iterations=0):
    # get the max_timeUnits number of a tweet propagation time (in 30 mins units)
    print "Calc max_timeUnits"
    if num_of_iterations == 0:  # we dont want to split it into batches, we want ALL of it
        max_timeUnits,counter_of_tweets_examined = extract_information([], [], 500, 3)  # it will return the maximum number of time units needed
    else:  # we want to split it into batches
        max_timeUnits,counter_of_tweets_examined = extract_information([], [], 500, 3, iteration_batches=iteration,
                                            total_iterations=num_of_iterations)  # it will return the maximum number of time units needed
    # initialization-create two lists values and numberOftweets and init them
    values = []
    numOftweets = []
    for x in range(0, max_timeUnits):
        values.append(0)  # on each row it has the sum of the number of retweets in the (rowNum) half-hour
        numOftweets.append(
            0)  # on each row has the number of tweets participated in values in order to calculate the avg

    if num_of_iterations == 0:  # we dont want to split it into batches, we want ALL of it
        extract_information(numOftweets, values, 500,
                            1)  # it will run the appropriate operations (operation_one()) in order to return the arrays numOftweets and values
    else:  # we want to split it into batches
        extract_information(numOftweets, values, 500,
                            1, iteration_batches=iteration,
                            total_iterations=num_of_iterations)  # it will run the appropriate operations (operation_one()) in order to return the arrays numOftweets and values
    # calculate average "" of tweets in that time interval
    avg = []
    counter = 0
    for i in values:
        if numOftweets[counter] != 0:
            avg.append(i / float(numOftweets[counter]))
        else:
            avg.append(0)
        counter = counter + 1
    #calculate the percentage change on this array of avgs
    # i=0
    # for item in avg:
    #     if item==0:
    #         avg[i]=1
    #     i=i+1
    percentage_difference=[]
    i=0
    for item in avg:
        if i!=0:
            if avg[i-1]!=0:
                difference=avg[i]-avg[i-1]
                per_chng=100.0*(difference/float(avg[i-1]))
                percentage_difference.append(per_chng)
            else:
                if avg[i]!=0:
                    percentage_difference.append(None)#100 ->alternative
                else:
                    percentage_difference.append(None)#0 ->alternative
        i=i+1
    avg=percentage_difference
    #Display the result
    xlim=0
    ylim=(-100,500)
    if show:
        if num_of_iterations == 0:  # we dont want to split it into batches, we want ALL of it
            plot_single_graph(avg, type, show,'Percentage change number of retweets', temp,counter_of_tweets_examined, filename='percentage_change_overall_{}mins',y_lim=ylim,x_lim=xlim)
        else:  # we want to split it into batches
            plot_single_graph(avg, type, show,'Percentage change number of retweets',  temp,counter_of_tweets_examined, filename='percentage_change_overall_{}mins',
                              iteration_batches=iteration, total_iterations=num_of_iterations,y_lim=ylim,x_lim=xlim)
    else:
        if num_of_iterations == 0:  # we dont want to split it into batches, we want ALL of it
            return plot_single_graph(avg, type, show, 'Percentage change number of retweets', [],counter_of_tweets_examined, filename='percentage_change_overall_{}mins',y_lim=ylim,x_lim=xlim)
        else:  # we want to split it into batches
            return plot_single_graph(avg, type, show, 'Percentage change number of retweets', [],counter_of_tweets_examined, filename='percentage_change_overall_{}mins',
                                     iteration_batches=iteration, total_iterations=num_of_iterations,y_lim=ylim,x_lim=xlim)

def number_of_retweets_distribution(type):
    print "Distribution of "+type
    arr=[]
    for og_tweet_collection in db.collection_names():  # for every tweet
        collection = db[og_tweet_collection]
        if og_tweet_collection != "users_info":
            cursor = collection.find({})  # Gets the tweets in that topic
            l=cursor.count()
            if l != 0 and l<=retweet_limit:
                arr.append(l)
    sns.set_style("whitegrid")
    colour = 'm'
    if type is "Fake":
        colour = '#1F77B4'
    else:
        colour = '#FF7F0F'

    # Cut the window in 2 parts
    f, (ax_box, ax_hist) = plt.subplots(2, sharex=True, gridspec_kw={"height_ratios": (.15, .85)})
    # Add a graph in each part
    sns.boxplot(arr, ax=ax_box,color=colour)
    sns.distplot(arr,bins=8, rug=True, ax=ax_hist,color=colour)
    # Remove x axis name for the boxplot
    ax_box.set(xlabel='')

    normalized_arr=preprocessing.normalize([arr])
    # fig=sns.distplot(arr,bins=8,kde=False, norm_hist=True);

    # fig = sns.kdeplot(arr, shade=True,hist=True)
    # plt.yticks(fig.get_yticks(), fig.get_yticks() * 100)
    ########################################
    # bins = np.arange(0,500, 60)
    # hist, edges = np.histogram(arr, bins)
    # freq = hist / float(hist.sum()######)
    # plt.bar(bins[:-1], freq, width=(500/len(bins))+3, align="edge",edgecolor='none',alpha=0.8)
    ########################################
    plt.xlabel('Number of retweets on a tweet chain')
    # plt.ylabel("Frequency")
    plt.title("Distribution of number of retweets on "+type+" news")
    filename="distribution_of_"+type+"_news"
    plt.savefig(dir + filename + savefiletype)
    plt.show()

def kde_plots(type, show,arr1,duration1):
    print "kde plots of "+type
    arr=[]
    diffusion_duration=[]
    for og_tweet_collection in db.collection_names():  # for every tweet
        collection = db[og_tweet_collection]
        if og_tweet_collection != "users_info":
            cursor = collection.find({})  # Gets the tweets in that topic
            l=cursor.count()
            if l != 0 and l<=retweet_limit:
                arr.append(l)
                #get the duration of the diffusion
                start_of_diffusion=datetime.now()
                end_of_diffusion=datetime.now()
                begin=True
                for document in cursor:
                    s = document["created_at"]
                    dt = datetime.now()
                    dt = dt.strptime(s, '%a %b %d %H:%M:%S +0000 %Y')
                    if begin:
                        begin=False
                        start_of_diffusion=dt
                        end_of_diffusion=dt
                    if dt<start_of_diffusion:
                        start_of_diffusion=dt
                    if dt>end_of_diffusion:
                        end_of_diffusion=dt
                duration=end_of_diffusion-start_of_diffusion
                diffusion_duration.append((duration.total_seconds()/60)/60)

    sns.set_style("whitegrid")
    #-----Density plot--------
    sns.distplot(arr,bins=8,rug=True);
    plt.xlabel('Number of retweets on a tweet chain')
    plt.title("Density plot of number of retweets on "+type+" news")
    filename="density_distribution_of_"+type+"_news"
    plt.savefig(dir + filename + savefiletype)
    plt.show()
    #------bivariate kde plot(diffusion time-number of retweets)-----
    colour='m'
    if type is "Fake":
        colour='#1F77B4'
    else:
        colour='#FF7F0F'
    # ax = sns.kdeplot(arr,diffusion_duration)


    ax = sns.jointplot(x=arr, y=diffusion_duration, kind="kde", color=colour,ylim=(0,600))
    ax.plot_joint(plt.scatter, c="w", s=30, linewidth=1, marker="+")
    ax.ax_joint.collections[0].set_alpha(0)
    ax.set_axis_labels("$X$", "$Y$");

    # ax.set(ylim=(0, 600))
    plt.xlabel('Number of retweets on a tweet chain')
    plt.ylabel('Total diffusion duration')
    plt.title("Marginal density plot of " + type + " news")
    filename = "marginal_densityPlot_of_" + type + "_news"
    plt.savefig(dir + filename + savefiletype)
    plt.show()
    # ------regression kde plot(diffusion time-number of retweets)-----
    if show:
        #-------------make a dataframe-------
        fakelistArray=['Fake']*len(arr1)
        reallistArray = ['Real'] * len(arr)
        fakeflag=fakelistArray+reallistArray
        number_of_retweets=arr1+arr
        duration_time=duration1+diffusion_duration
        d = {'retweetNum': number_of_retweets, 'duration': duration_time,'veracity':fakeflag}
        df = pd.DataFrame(data=d)
        #-----------end with make dataframe
        ax = sns.lmplot(x="retweetNum", y="duration", hue="veracity", data=df)
        ax.set(ylim=(0, 2000))
        plt.xlabel('Number of retweets on a tweet chain')
        plt.ylabel('Total diffusion duration')
        plt.title("Regression of Real and Fake news")
        filename = "regression"
        plt.savefig(dir + filename + savefiletype)
        plt.show()
    else:
        return arr, diffusion_duration

def scatter_plots(language):
    dataFake=[]
    indexFake=[]
    dataReal = []
    indexReal = []
    db = client[fake]
    type="Fake"
    f=True
    print f
    while(f==True):
        c=0
        for og_tweet_collection in db.collection_names():
            c=c+1
            if c<=550:
                collection = db[og_tweet_collection]
                if og_tweet_collection != "users_info":
                    cursor = collection.find({})
                    try:
                        status = api.get_status(id=og_tweet_collection)
                        sourceName = status.user.screen_name
                    except:
                        sourceName="Deleted"
                    print sourceName,c
                    number_of_retweets = cursor.count()
                    if type is "Fake":
                        indexFake.append(sourceName)
                        dataFake.append(number_of_retweets)
                    else:
                        indexReal.append(sourceName)
                        dataReal.append(number_of_retweets)
        print f
        if type is "Real":
            f=False
        else:
            db = client[real]
            type = "Real"
        print f,"should have changed", type
    data=dataFake+dataReal
    indexToChange=indexFake+indexReal
    index=[]

    for word in indexToChange:
        newWord=""
        if "_" in word:
            newWord=word.replace("_", "\_")
        else:
            newWord=word
        if language is "greek":
            index.append(r"\textlatin{" + newWord + "}")
        else:
            index.append(newWord)
    fakelistArray = ['Fake'] * len(dataFake)
    reallistArray = ['Real'] * len(dataReal)
    fakeflag = fakelistArray + reallistArray
    d_general = {'retweetNum': data, 'tweetname': index, 'veracity': fakeflag}
    d_fake = {'retweetNum': dataFake, 'tweetname': indexFake, 'veracity': fakelistArray}
    d_real = {'retweetNum': dataReal, 'tweetname': indexReal, 'veracity': reallistArray}
    plot_a_scatter_plot("general",language,d_general)
    # plot_a_scatter_plot("general", language, d_fake)
    # plot_a_scatter_plot("general", language, d_real)


def plot_a_scatter_plot(type,language,d):
    new_rc_params = {
        "font.family": 'Times',
        # probably python doesn't know Times, but it will replace it with a different font anyway. The final decision is up to the latex document anyway
        "font.size": 6,  # choosing the font size helps latex to place all the labels, ticks etc. in the right place
        "font.serif": [],
        "svg.fonttype": 'none'}  # to store text as text, not as path
    matplotlib.rcParams.update(new_rc_params)
    filename = "scatter_plot_general" + "_" + language
    if type != "general":
        filename = "scatter_plot_of_" + type + "_news" + "_" + language

    markers = {"Fake": "s", "Real": "X"}
    ax = sns.scatterplot(x='tweetname', y='retweetNum', hue='veracity', data=d)

    plt.xticks(rotation=90)
    plt.ylim(-40, 2000)
    plt.xlabel('User')
    plt.ylabel("Number of retweets")
    plt.title("Scatter plot of the tweet collection")
    plt.savefig(dir + filename + savefiletype)
    print dir+filename+savefiletype
    plt.show()





#________________EXECUTION SEGMENT_______________
#In order to get a certain figure, simply uncomment the appropriate segment

# minutes_list=[5,10,15,20,25,30]
minutes_list=[30]
show_once_flag=True

for i in minutes_list:
    mins=i
    # # ~~~~~~~~~~~~~title:Overall~~~~~~~~~~~~~ 1 figure
    # db = client[fake]
    # temp=overall_figure("Fake",False,[])
    # db = client[real]
    # overall_figure("Real",True,temp)
    # #~~~~~~~~~~~~~title:Overall In Batches~~~~~~~~~~~~~ Multiple figure
    # num_of_iterations=(retweet_limit/split_per_retweetNumber)-1#has to calculate the number of batched it will create
    # iter=0
    # while(iter<=num_of_iterations):
    #     db = client[fake]
    #     temp=overall_figure("Fake",False,[],iteration=iter,num_of_iterations=num_of_iterations)
    #     db = client[real]
    #     overall_figure("Real",True,temp,iteration=iter,num_of_iterations=num_of_iterations)
    #     iter = iter + 1
    # #~~~~~~~~~~~~~title:Overall with Boxplots~~~~~~~~~~~~~ 2 figures
    # twoDarrayForOperationFive=[]
    # db = client[fake]
    # overall_boxplot_figure("Fake")
    # twoDarrayForOperationFive=[]
    # db = client[real]
    # overall_boxplot_figure("Real")
    # #~~~~~~~~~~~~~title:Overall with Boxplots with bathces~~~~~~~~~~~~~Multiple figures
    # num_of_iterations=(retweet_limit/split_per_retweetNumber)-1#has to calculate the number of batched it will create
    # iter=0
    # while(iter<=num_of_iterations):
    #     twoDarrayForOperationFive=[]
    #     db = client[fake]
    #     overall_boxplot_figure("Fake",iteration=iter,num_of_iterations=num_of_iterations)
    #     twoDarrayForOperationFive=[]
    #     db = client[real]
    #     overall_boxplot_figure("Real",iteration=iter,num_of_iterations=num_of_iterations)
    #     iter = iter + 1
    # #~~~~~~~~~~~~~title:Overall Percent Change~~~~~~~~~~~~~ 1 figure
    # db = client[fake]
    # temp=overall_percentages_change("Fake",False,[])
    # db = client[real]
    # overall_percentages_change("Real",True,temp)
    # #~~~~~~~~~~~~~title:Overall Percent Change In Batches~~~~~~~~~~~~~ Multiple figure
    # num_of_iterations=(retweet_limit/split_per_retweetNumber)-1#has to calculate the number of batched it will create
    # iter=0
    # while(iter<=num_of_iterations):
    #     db = client[fake]
    #     temp=overall_percentages_change("Fake",False,[],iteration=iter,num_of_iterations=num_of_iterations)
    #     db = client[real]
    #     overall_percentages_change("Real",True,temp,iteration=iter,num_of_iterations=num_of_iterations)
    #     iter = iter + 1
    #~~~~~PLOTS THAT SHOULD BE PRINTED ONLY ONCE~~~~~~~~~~~~~
    if show_once_flag:
        show_once_flag=False
        # # ~~~title:Distribution Plot~~~~~~~~~~~~~
        # db = client[fake]
        # number_of_retweets_distribution("Fake")
        # db = client[real]
        # number_of_retweets_distribution("Real")
        # ~~~title:KDE Plots~~~~~~~~~~~~~
        # db = client[fake]
        # a,b=kde_plots("Fake",False,[],[])
        # db = client[real]
        # kde_plots("Real",True,a,b)
        # ~~~title:scatter Plots~~~~~~~~~~~~~
        scatter_plots("english")
        # # ~~~~~~~~~~~~title:Completion of DB processing~~~~~~~~~~~~~~ 2 figures
        # comparisson_set = set()
        # # db = client[fake]
        # # comparisson_set = completion_DB_processing("Fake", comparisson_set)
        # db = client[real]
        # completion_DB_processing("Real", comparisson_set)
        # # ~~~~~~~~~~~~title:Friends/Followers Ratio~~~~~~~~~~~~~~ 1 figure
        # db = client[fake]
        # temp = friend_follower_ratio("fake", False, [])
        # db = client[real]
        # friend_follower_ratio("real", True, temp)
        # # ~~~~~~~~~~~~~title:Individual~~~~~~~~~~~~~ 2 figures
        # db = client[fake]
        # individual_fugures("Fake")
        # db = client[real]
        # individual_fugures("Real")
        # # ~~~~~~~~~~~~~title:Verified Users~~~~~~~~~~~~~ 2 figures
        # db = client[fake]
        # graphs_of_verified_users("Fake")
        # db = client[real]
        # graphs_of_verified_users("Real")
        # # ~~~~~~~~~~~~title:CDF~~~~~~~~~~~~~~ 1 figure
        # db = client[fake]
        # temp = cdf("fake", False, [])
        # db = client[real]
        # cdf("real", True, temp)
        # # ~~~~~~~~~~~~title:CDF with batches~~~~~~~~~~~~~~ Multiple figure
        # num_of_iterations = (retweet_limit / split_per_retweetNumber) - 1  # has to calculate the number of batched it will create
        # iter = 0
        # while (iter <= num_of_iterations):
        #     db = client[fake]
        #     temp = cdf("fake", False, [], iteration=iter, num_of_iterations=num_of_iterations)
        #     db = client[real]
        #     cdf("real", True, temp, iteration=iter, num_of_iterations=num_of_iterations)
        #     iter = iter + 1




