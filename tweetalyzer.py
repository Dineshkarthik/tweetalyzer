"""Import the necessary methods from tweepy library."""
import redis
import yaml
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from http.client import IncompleteRead
from rq import Queue
from tweetprocessor import process_tweet

# User credentials to access Twitter API
f = open('config.yaml')
twitter_config = yaml.safe_load(f)
f.close()

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
q = Queue(connection=redis.Redis())
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


class StdOutListener(StreamListener):
    """This is a basic listener that receives tweets."""

    def on_data(self, data):
        """Function that enqueues tweets to RabbitQ."""
        q.enqueue(process_tweet, data)
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
    while True:
        try:
            stream = Stream(auth, l)
            stream.filter(track=[
                'anime', 'manga', 'naruto', 'dragonball', 'dragon ball', 'dbz',
                'bleach', 'goku', 'vegeta', 'tokyo ghoul', 'attack on titans',
                'one piece', 'luffy'
            ])
        except IncompleteRead:
            continue
        except KeyboardInterrupt:
            stream.disconnect()
            break
