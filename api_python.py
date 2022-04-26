from flask import Flask, render_template, request, send_file
import praw
import json

from recommenderSystemV2.recommenderv2 import recommend
from chat import chat

import pandas as pd
import numpy as np
from io import BytesIO
from joblib import load
import matplotlib.pyplot as plt

from topic_modeling.api import ApiObject

# model_sentiment = load("models/modelsentiment.pkl_jlib")

topic_api = ApiObject()

r = praw.Reddit(
    client_id="/",
    client_secret="/",
    user_agent="SDSC project for reddit")


WINDOW_FOR_ZSCORE = 5
MIN_ZSCORE = 2

# Create the application instance
app = Flask(__name__)


@app.route('/recommend/subreddits/<refreshToken>', methods=['POST'])
def recommendV2(refreshToken):
    reddit = praw.Reddit(client_id="qvMRnp43GrAkgw",
        client_secret="2ihfHsjEa4UpPEQJ8GOvnu8C8_M",
        refresh_token=refreshToken,
        user_agent="ScrapXPost"
    )

    print([i.display_name for i in reddit.user.subreddits()])

    return json.dumps(recommend([i.display_name for i in reddit.user.subreddits()], []))



@app.route('/analysis/sentiment', methods = ['POST'])
def sentiment_analysis():
    txt = request.json['text']
    return json.dumps({"sentiment": int(model_sentiment.predict([txt])[0])})


@app.route('/user/getSubreddits/<refreshToken>', methods = ['GET'])
def get_subreddits(refreshToken):
    reddit = praw.Reddit(client_id="/",
        client_secret="/",
        refresh_token=refreshToken,
        user_agent="ScrapXPost"
    )
    return json.dumps({"followed_subs": [i.display_name for i in reddit.user.subreddits()]})


## topic modeling

@app.route('/topics/subreddit', methods = ['POST'])
def get_subreddit_topics(): # request example {"name" : "sub_name"}
    data = request.json

    if 'name' in data:
        sub_name = data['name']
        prediction = topic_api.get_subreddit_topic(sub_name)
        return prediction
    else:
        return topic_api.format_response(topics=None, error=True)

@app.route('/topics/submission', methods = ['POST'])
def get_submission_topics(): # request example {"id" : "submission_id"}
    data = request.json

    if 'id' in data:
        submission_id = data['id']
        prediction = topic_api.get_submission_topic(submission_id)
        return prediction
    else:
        return topic_api.format_response(topics=None, error=True)

@app.route('/topics/subreddit_recommendation_from_sub', methods = ['POST'])
def get_recommendations_from_sub(): # request example {"name" : "sub_name", "top": 5}
    data = request.json

    if 'name' in data:
        if 'top' in data:
            recommendation = topic_api.recommand_subreddit_by_name(data['name'], data['top'])
        else:
            recommendation = topic_api.recommand_subreddit_by_name(data['name'])
        return recommendation
    else:
        return topic_api.format_response(topics=None, error=True)

@app.route('/topics/subreddit_recommendation_from_data', methods = ['POST'])
def get_recommendations_from_data(): # request example {"data" : ["football", "sport"], "top": 5}
    data = request.json

    if 'data' in data:
        if 'top' in data:
            recommendation = topic_api.recommand_subreddit_from_keywords(data['data'], data['top'])
        else:
            recommendation = topic_api.recommand_subreddit_from_keywords(data['data'])
        return recommendation
    else:
        return topic_api.format_response(topics=None, error=True)

@app.route('/topics/Aio35uB7Di6qubzD3q615EQ', methods = ['POST'])
def drop_database(): # request example {"data" : ["football", "sport"], "top": 5}
    return topic_api.reset_db()

@app.route('/topics/count_subreddits', methods = ['GET'])
def count_subs_in_db(): # request example {"data" : ["football", "sport"], "top": 5}
    # return topic_api.count_subs()
    return "test"

##end topic modeling

@app.route('/trends/get_trends')    # retourne les subs en tendance
def get_trends():
    df = pd.read_csv('post_per_day_by_subs.csv')
    tmp=df.apply(lambda x: zscore(x, WINDOW_FOR_ZSCORE))
    r=tmp[tmp>MIN_ZSCORE]
    return json.dumps({"trends":[{"name":i, "r_score":r[i], "daily_values":list(df[i])} for i in r.index]})



@app.route('/trends/draw', methods = ['POST'])
def trends_analysis():
    plt.figure()
    L = pd.Series(request.form['num'])
    moyMob = L.rolling(window=WINDOW_FOR_ZSCORE).mean().shift(1)[WINDOW_FOR_ZSCORE:]
    ecaMob = L.rolling(window=WINDOW_FOR_ZSCORE).std(ddof=0).shift(1)[WINDOW_FOR_ZSCORE:]
    L = L[WINDOW_FOR_ZSCORE:]
    plt.plot(L, label="Nombre de posts journaliers")
    plt.plot(moyMob, label="Moyenne mobile")
    plt.fill_between(
        L.index,
        moyMob + ecaMob,
        moyMob - ecaMob,
        color='g',
        alpha=0.3,
        label='Ecart-type mobile')
    plt.fill_between(L.index,
                     L, 
                     moyMob + ecaMob,
                     where=L >= moyMob + ecaMob, facecolor='red', interpolate=True, 
                    label='Trending')
    plt.legend()
    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')


@app.route('/chatbot', methods = ['POST'])
def chatbot_response():
    txt = request.json['text']
    return json.dumps(chat(txt))
    # return json.dumps({"message": "vous avez dit : "+txt})


def zscore(x, window):
    r = x.rolling(window=window)
    m = r.mean().shift(1)
    s = r.std(ddof=0).shift(1)
    z = (x-m)/s
    return z.to_numpy()[-1]


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True)