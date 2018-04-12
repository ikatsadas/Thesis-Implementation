from datetime import datetime,timedelta
import pymongo
from pymongo import MongoClient
import matplotlib
import matplotlib.pyplot as plt
import numpy as np



# uri = "mongodb://user:SpYZ7EMlgs@snf-795686.vm.okeanos.grnet.gr:25"
client = MongoClient('localhost', 27017)
# client = MongoClient(uri)
db = client['getMostRetweetedFake']

mins=600

def overall_figure():
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
            if max_timeUnits<len(x):  # initialization
                print max_timeUnits, "cahnged to ", len(x)
                max_timeUnits = len(x)
    #############################################
    print "calc values"
    #initialization
    values=[]
    numOftweets=[]
    for x in range(0, max_timeUnits):
        values.append(0)
        numOftweets.append(0)

    c=0
    for og_tweet_collection in db.collection_names():  # for every tweet
        c=c+1
        if c>90:
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
                values[counter]=values[counter]+i/float(len(retweet_time))
                numOftweets[counter] = numOftweets[counter] + 1#keep track of how many tweets's retweets are in that position
                counter=counter+1
    #calculate average frequency of tweets in that time interval
    avg=[]
    counter=0
    for i in values:
        if numOftweets[counter]!=0:
            avg.append(i/float(numOftweets[counter]))
        else:
            avg.append(0)
        counter=counter+1

    #plot
    avg_np = np.array(avg)
    plt.plot(avg_np,'b--')
    plt.xlabel('Time')
    plt.ylabel('# of retweets')
    plt.ylim(0,0.005)
    plt.xlim(0,750)
    plt.title('retweets in time')
    plt.show()
#############################################

def individual_fugures():
    c=0
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
                c_time=start_date + timedelta(minutes=30 * it)
                # print c_time.strftime("%Y-%m-%d,%H:%M")
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
                print i

                values[counter]=i/float(len(retweet_time))
                print values[counter]
                counter=counter+1
            dates = matplotlib.dates.date2num(x)
            plt.plot_date(dates, values,'r--')
            # xv = np.array(retweet_time)
            # plt.plot(xv)
            plt.xlabel('Time')
            plt.xticks(rotation=30)
            plt.ylabel('# of retweets')
            plt.title('retweets in time')
            plt.show()

overall_figure()
# individual_fugures()