"""Import the necessary methods from tweepy library."""
import redis
import yaml
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime, timedelta
from tweetprocessor import process_tweet
import threading

# User credentials to access Twitter API
f = open('config.yaml')
twitter_config = yaml.safe_load(f)
f.close()

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
if not r.exists("stats"):
    r.set("tweet_count", 0)
    r.hmset("stats", {
        'lang': {},
        'tweet_count': 0,
        'word_cloud': {},
        'hashtags': {},
        'users': {},
        'date': {},
        'day': {},
        'hour': {},
        'loc': {}
    })


def init_task():
    """Function to schedule minute wise tweet ingestion."""
    file = (datetime.now() - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M")
    process_tweet.apply_async(args=[file])
    threading.Timer(60.0, init_task).start()


class StdOutListener(StreamListener):
    """This is a basic listener that receives tweets."""

    def on_data(self, data):
        """Function that enqueues tweets to rq."""
        datetime_object = datetime.now()
        file = datetime_object.strftime("%Y-%m-%dT%H:%M")
        with open(file, 'a+') as f:
            f.write(data)

        return True

    def on_error(self, status):
        """Print error status."""
        print(status)


if __name__ == '__main__':

    l = StdOutListener()
    auth = OAuthHandler(twitter_config["consumer_key"],
                        twitter_config["consumer_secret"])
    auth.set_access_token(twitter_config["access_token"],
                          twitter_config["access_token_secret"])
    threading.Timer(60.0, init_task).start()
    while True:
        try:
            stream = Stream(auth, l)
            stream.filter(track=['anime'])
        except KeyboardInterrupt:
            stream.disconnect()
            break
        except:
            continue
