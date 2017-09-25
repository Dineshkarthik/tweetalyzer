# Tweetalyzer

Tweetalyzer is a simple  Python app to Stream and Visualise Tweets on specific topics.
Visualisation - Work In Progress.

### Tech

Tweetalyzer uses a number of open source projects to work properly:

* [Flask] - microframework for Python based on Werkzeug, Jinja 2.
* [Pandas] - pandas is an open source, library providing high-performance, easy-to-use data structures and data analysis tools for the Python.
* [Redis] - Redis is an open source, in-memory data structure store, used as a database, cache and message broker.
* [Celery] - Celery is an asynchronous task queue/job queue based on distributed message passing.
* [TextBlob] - TextBlob is a Python (2 and 3) library for processing textual data.
* [Tweepy] - An easy-to-use Python library for accessing the Twitter API.

### Installation

You need Python 3.*, its dependency packages, and the above mentioned packages installed globally:
```sh
$ git clone https://github.com/Dineshkarthik/tweetalyzer.git
$ cd tweetalyzer
$ pip install -r requirements.txt
```

### Execution
```sh
$ python tweetalyzer.py
$ python server.py
$ celery -A tweetprocessor worker --loglevel=info
```
* Running `tweetalyzer.py` will start streaming the tweets in the specified topics and will store them in text files.
* Running `sever.py` will start the flask server and the visualisation can be accessed at `http://localhost:5000` 
* server.py will start the flask server in port 5000 by default which can be started in any other port like `python server.py -p 8000`
* Command `celery -A tweetprocessor worker --loglevel=info` will start the celery workers which will start processing the stored tweets, which happens every one minute.
