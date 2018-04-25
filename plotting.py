from datetime import datetime,timedelta
import pymongo
from pymongo import MongoClient
import matplotlib
import matplotlib.pyplot as plt
import numpy as np



# uri = "mongodb://user:SpYZ7EMlgs@snf-795686.vm.okeanos.grnet.gr:25"
client = MongoClient('localhost', 27017)
# client = MongoClient(uri)
db = client['getMostRetweetedTest']

mins=30# number of minutes for the time interval

def overall_figure():
    ###########################################################################
    #get the max_timeUnits number of a tweet propagation time (in 30 mins units)
    print "Calc max_timeUnits"
    c=0
    max_timeUnits=0
    for og_tweet_collection in db.collection_names():  # for every tweet
        c = c + 1
        collection = db[og_tweet_collection]
        cursor = collection.find({})  # Gets the tweets in that topic
        retweet_time = []
        for document in cursor:
            s = document["created_at"]
            dt = datetime.now()
            dt = dt.strptime(s, '%a %b %d %H:%M:%S +0000 %Y')
            retweet_time.append(dt)
        if len(retweet_time) != 0:
            retweet_time = sorted(retweet_time)
            start_date = retweet_time[0]
            end_date = retweet_time[-1]
            c_time = start_date
            x = []
            it = 0
            while (c_time < end_date):
                c_time = start_date + timedelta(minutes=mins * it)
                x.append(c_time)
                it = it + 1
            if max_timeUnits<len(x):  # initialization-get the biggest number of time intervals
                print max_timeUnits, "cahnged to ", len(x)
                max_timeUnits = len(x)
        else:
            c=c-1
    #############################################
    print "calc values"
    #initialization-create two lists values and numberOftweets and init them
    values=[]
    numOftweets=[]
    for x in range(0, max_timeUnits):
        values.append(0)#on each row it has the sum of the number of retweets in the (rowNum) half-hour
        numOftweets.append(0)#on each row has the number of tweets participated in values in order to calculate the avg

    c=0
    for og_tweet_collection in db.collection_names():  # for every tweet
        c=c+1
        if c>250:
            break
        collection = db[og_tweet_collection]
        cursor = collection.find({})  # Gets the tweets in that topic
        retweet_time = []
        #get all the retweets
        for document in cursor:
            s=document["created_at"]
            dt=datetime.now()
            dt = dt.strptime(s, '%a %b %d %H:%M:%S +0000 %Y')
            retweet_time.append(dt)#add the time of the retweet to an array
        if len(retweet_time)!=0:# if the tweet had retweets
            retweet_time = sorted(retweet_time)#sort chronologically
            #get the number of time intervals (of 30 minutes)
            start_date = retweet_time[0]
            end_date=retweet_time[-1]
            c_time=start_date
            x=[]
            it=0
            while(c_time<end_date):
                c_time=start_date + timedelta(minutes=mins * it)
                x.append(c_time)#store the start of every time interval in x array
                it=it+1
            #initialization
            s=x[0]
            e=x[1]
            pointer=0
            v = []
            for i in x:
                v.append(0)
            #fill v array with the number of retweets happened in a specific time interval
            for i in retweet_time:
                if i>e:
                    flag=True
                    while flag:
                        pointer=pointer+1
                        if pointer>len(x)-1:
                            break
                        s=x[pointer]
                        e=x[pointer+1]
                        if e >= i >= s:
                            flag=False
                if e >= i >= s:
                    v[pointer]=v[pointer]+1
            #Now we know how many retweets happened each 30 minutes (in v array)
            counter=0
            for i in v:#add the avg frequency of the tweet in the corresponding 30 minutes
                # values[counter]=values[counter]+i/float(len(retweet_time)) #<--for frequency of tweets
                values[counter] = values[counter] + i #<--for getting the avg number of tweets
                numOftweets[counter] = numOftweets[counter] + 1#keep track of how many tweets's retweets are in that position
                counter=counter+1
        else:
            c=c-1
    #calculate average "" of tweets in that time interval
    avg=[]
    counter=0
    for i in values:
        if numOftweets[counter]!=0:
            avg.append(i/float(numOftweets[counter]))
        else:
            avg.append(0)
        counter=counter+1

    #plot
    avg=avg[:500] #trimming the list
    avg_np = np.array(avg)
    plt.plot(avg_np,'-')
    plt.xlabel('Time(# of 30 mins intervals)')
    plt.ylabel('Average # of retweets')
    # plt.ylim(0,0.005)
    # plt.xlim(0,750)
    plt.title('Average propagation of FAKE news in Twitter')
    plt.show()
#############################################

def individual_fugures():
    c=0
    f, axarr = plt.subplots(2, 5,sharex=True,sharey=True)
    matplotlib.rcParams.update({'font.size': 5})
    for og_tweet_collection in db.collection_names():  # for every tweet
        c=c+1
        if c>10:
            break
        collection = db[og_tweet_collection]
        cursor = collection.find({})  # Gets the tweets in that topic
        retweet_time = []
        for document in cursor:
            s=document["created_at"]
            dt=datetime.now()
            dt = dt.strptime(s, '%a %b %d %H:%M:%S +0000 %Y')
            retweet_time.append(dt)
        if len(retweet_time)!=0:
            retweet_time = sorted(retweet_time)
            start_date = retweet_time[0]
            end_date=retweet_time[-1]
            c_time=start_date
            x=[]
            it=0
            while(c_time<end_date):
                c_time=start_date + timedelta(minutes=mins * it)
                x.append(c_time)
                it=it+1

            s=x[0]
            e=x[1]
            pointer=0
            values=[]
            for i in x:
                values.append(0)
            for i in retweet_time:
                if i>e:
                    flag=True
                    while flag:
                        pointer=pointer+1
                        if pointer>len(x)-1:
                            break
                        s=x[pointer]
                        e=x[pointer+1]
                        if e >= i >= s:
                            flag=False
                if e >= i >= s:
                    values[pointer]=values[pointer]+1

            counter=0
            for i in values:
                values[counter]=i/float(len(retweet_time))
                counter=counter+1
            dates = matplotlib.dates.date2num(x)
            if c<=5:
                k=0
                l=c-1
            else:
                k=1
                l=c-6
            # axarr[k, l].plot_date(dates, values, 'r--')
            #trim the list to a smaller time interval
            if(len(values)>30):
                values=values[:30]
            axarr[k, l].plot(values,'r')
            axarr[k, l].set_title(og_tweet_collection)
            # plt.subplot(2, 5, c)
            # plt.xticks(rotation=30)
            # plt.ylabel('Frequency of retweets')
            # plt.title(str(c))#tweet ID
            # plt.plot_date(dates, values, 'r--')
            plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.1, hspace=0.2)
        else:
            c=c-1
    for ax in axarr.flat:
        ax.set(xlabel='# of 30 mins', ylabel='Frequency of retweets')
        ax.label_outer()
    for ax in f.axes:
        matplotlib.pyplot.sca(ax)
        plt.xticks(rotation=30)
    plt.suptitle("Propagation of FAKE news tweets")
    plt.show()


def graphs_of_verified_users():
    f, axarr = plt.subplots(2, 5, sharex=True, sharey=True)
    matplotlib.rcParams.update({'font.size': 5})
    c = 0
    for og_tweet_collection in db.collection_names():  # for every tweet
        collection = db[og_tweet_collection]
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
                while (c_time < end_date):
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

                counter = 0
                for i in values:
                    values[counter] = i / float(len(retweet_time))
                    counter = counter + 1
                dates = matplotlib.dates.date2num(x)
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
                # plt.subplot(2, 5, c)
                # plt.xticks(rotation=30)
                # plt.ylabel('Frequency of retweets')
                # plt.title(str(c))#tweet ID
                # plt.plot_date(dates, values, 'r--')
                plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.1, hspace=0.2)
            else:
                c = c - 1
    for ax in axarr.flat:
        ax.set(xlabel='# of 30 mins', ylabel='Frequency of retweets')
        ax.label_outer()
    for ax in f.axes:
        matplotlib.pyplot.sca(ax)
        plt.xticks(rotation=30)
    plt.suptitle("Propagation of FAKE news tweets")
    plt.show()

# overall_figure()
# individual_fugures()
# graphs_of_verified_users()


