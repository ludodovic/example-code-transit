# from psaw import PushshiftAPI
import praw
import json
import numpy as np
import datetime as dt
import pandas as pd
import math
from collections import Counter

r_api = praw.Reddit(
    client_id = "/",
    client_secret = "/",
    user_agent = "SDSC project for reddit"
)
# api = PushshiftAPI(r)

def fun (b, a):
    if math.isnan(b):
        return a
    else:
        return b + a

f  = np.vectorize(fun, otypes = [float])



def getUserActivityFromList(username, list_of_subs):
    return pd.DataFrame([[1]*len(list_of_subs)], index = [username], columns = list_of_subs)


def getUserActivity(username):
    rer = pd.DataFrame()
    user = r_api.redditor(username)
    comment = user.comments.new(limit = None)
    submissions = user.submissions.new(limit = None)
    sub = []
    com_list = []

    for link in submissions:
        sub.append(link.subreddit)

    for link in comment:
        com_list.append(link.subreddit)
    list_sub = list(Counter(sub).keys())
    list_unique_sub = []

    for i in range (0,len(list_sub)):
        list_unique_sub.append(list_sub[i].display_name)
    count_sub = list(Counter(sub).values())
    list_com = list(Counter(com_list).keys())
    list_unique_com = []

    for i in range (0,len(list_com)):
        list_unique_com.append(list_com[i].display_name)
    count_com = list(Counter(com_list).values())

    res =  pd.DataFrame(count_sub,list_unique_sub,columns  = ['submission'])
    res = res.fillna(0)

    result =  pd.DataFrame(count_com,list_unique_com,columns  = ['comment'])
    result = result.fillna(0)

    rer = pd.concat([res, result], axis = 1, sort = False)
    rer = rer.fillna(0)

    rer[username] = f(rer['comment'],rer['submission'] )
    rer = rer[[username]]

    print(rer)
    return rer

def getUserActivity_old(username):
    res = pd.DataFrame()
    result = api.redditor_subreddit_activity(username)
    df = pd.DataFrame.from_dict(result)
    df[username] = f(df['comment'], df['submission'])
    df = df[[username]]
    res = pd.concat([res, df], axis = 1, sort = False)
    return res

