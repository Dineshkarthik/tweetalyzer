"""Simple Flask server which runs the frontend."""
import ast
import redis
import pandas as pd
from flask import Flask, render_template
from optparse import OptionParser


app = Flask(__name__)

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


@app.route("/", methods=['GET', 'POST'])
def index():
    """Function that render index html page."""
    dict_ = {}
    dict_["tweet_count"] = r.get("tweet_count")
    dict_["day"] = ast.literal_eval(r.hget("stats", "day"))
    dict_["date"] = ast.literal_eval(r.hget("stats", "date"))
    for key in ['lang', 'word_cloud', 'hashtags', 'users', 'loc']:
        rs = ast.literal_eval(r.hget("stats", key))
        dict_[key] = ((pd.Series(rs)).sort_values(
            axis=0, ascending=False, inplace=False)[:5]).to_dict()
    return render_template('index.html', data=dict_)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
        "-p",
        "--port",
        dest="port",
        help="Port on which the app will run",
        default=5000)
    (options, args) = parser.parse_args()
    app.run(host='0.0.0.0', debug=True, port=int(options.port))
