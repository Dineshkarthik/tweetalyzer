"""Script that analysis and stores the tweets."""
import json
import re
import ast
import redis
import os
from datetime import datetime
from textblob import TextBlob
from celery import Celery


application = Celery('tasks', broker='redis://localhost:6379/2')


r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
text_file = open("stop_words.txt", "r")
stop_words = text_file.read().split(',')
text_file.close()


def to_dict(data):
    """Function to normalise the data received from Stream API."""
    d = json.loads(data)
    dict_ = {}
    dict_["user_time_zone"] = d["user"]["time_zone"]
    dict_["loc"] = d["user"]["location"]
    dict_["text"] = d["text"]
    dict_["lang"] = d["lang"]
    dict_["coords"] = d["coordinates"]
    dict_["user_id"] = d["user"]["id"]
    dict_["name"] = d["user"]["name"]
    dict_["screen_name"] = d["user"]["screen_name"]
    dict_["id_str"] = d["id_str"]
    dict_["created"] = d["created_at"]
    dict_["retweets"] = d["retweet_count"]
    dict_["hashtags"] = [x['text'] for x in d["entities"]["hashtags"]]
    dict_["user_mentions_name"] = [
        x['name'] for x in d["entities"]["user_mentions"]
    ]
    dict_["user_mentions_screen_name"] = [
        x['screen_name'] for x in d["entities"]["user_mentions"]
    ]
    dict_["country"] = d['place']['country'] if d[
        'place'] is not None else None
    datetime_object = datetime.strptime(d["created_at"],
                                        "%a %b %d %H:%M:%S %z %Y")
    dict_["date"] = datetime_object.strftime("%Y-%m-%d")
    dict_["day"] = datetime_object.strftime("%A")
    dict_["hour"] = datetime_object.strftime("%H")
    return dict_


def word_list(text):
    """Function to get list of words ignoring stopwords."""
    words = []
    text = re.sub(r'[?|$|.|!-/]', r'', text.lower())
    for word in text.split():
        if word.startswith(("http", "@", "#")):
            continue
        if word not in stop_words:
            words.append(word)
    return words


def calc(key, dict_):
    """Function to calculate frequency."""
    temp_dict = ast.literal_eval(str(dict_))
    if key in temp_dict:
        temp_dict[key] = temp_dict[key] + 1
    else:
        temp_dict[key] = 1
    return temp_dict


@application.task
def process_tweet(filename):
    """Funciton to process the tweets received from Twitter Stream."""
    with open(filename) as lines:
        for line in lines:
            dict_ = to_dict(line)
            blob = TextBlob(dict_["text"])
            lang = blob.detect_language()
            if not (lang == "en"):
                try:
                    dict_["text"] = str(blob.translate(to="en"))
                except Exception:
                    pass
            r.incr("tweet_count")
            stats = r.hgetall("stats")
            stats["lang"] = calc(lang, stats["lang"])
            stats["date"] = calc(dict_["date"], stats["date"])
            stats["day"] = calc(dict_["day"], stats["day"])
            stats["hour"] = calc(dict_["hour"], stats["hour"])
            for hashtag in dict_["hashtags"]:
                stats["hashtags"] = calc(hashtag.lower(), stats["hashtags"])

            stats["users"] = calc(dict_["screen_name"], stats["users"])
            words_list = word_list(dict_["text"])
            for word in words_list:
                stats["word_cloud"] = calc(word, stats["word_cloud"])

            r.hmset("stats", stats)
    os.remove(filename)
