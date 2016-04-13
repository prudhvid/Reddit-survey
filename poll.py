"""
The server for Reddit poll
"""
import json
from datetime import datetime
import sqlite3
from contextlib import closing
from flask import Flask, render_template, request, send_from_directory
from flask import g, url_for
from numpy import base_repr

app = Flask(__name__, static_url_path="")

"""
 create table user(
   roll text primary key,
   name text);
 create table survey(
   user text,
   subreddit text,
   value integer);
"""

DATABASE = "./data.sqlite3"

SUBREDDIT_FILE = "./final_subs.txt"

USER_JSONFILE = './user-reddit.json'

POSTS_LINK_FILE = './final_post_data.json'

DEFAULT_PARAMS = {
    "survey": {
        "title": "Identifying sources of value for subreddits",
        "description": (
            "Survey on categorizing post-based/comment-based subreddits"
            "in Reddit."),
    }
}


post_link_data = {}

with open(POSTS_LINK_FILE) as pobj:
    post_link_data = json.load(pobj)


with open(SUBREDDIT_FILE) as fobj:
    subreddits = fobj.read().split()


def read_json():
    """Read the json file to get key_data information"""
    global key_data
    with open(USER_JSONFILE) as fobj:
        key_data = json.load(fobj)

read_json()


def connect_db():
    """Simple connection to sqlite databse"""
    return sqlite3.connect(DATABASE)


def init_db():
    """Initalize db -- call from main initally """
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as fobj:
            db.cursor().executescript(fobj.read())
        db.commit()


@app.before_request
def before_request():
    """connect to db and close connection at the end"""
    g.db = connect_db()


@app.after_request
def after_request(response):
    """connect to db and close connection at the end"""
    g.db.close()
    return response


def query_db(query, args=(), one=False):
    """custom query wrapper over raw query"""
    cur = g.db.execute(query, args)
    g.db.commit()
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


@app.route('/components/<path:path>')
def send_js(path):
    """serve static files"""
    return send_from_directory('bower_components', path)


@app.route('/css/<path:path>')
def send_css(path):
    """serve static files"""
    return send_from_directory('css', path)



@app.route('/')
def root():
    """Base url display instructions for user with key c"""
    params = dict(DEFAULT_PARAMS)
    key = request.args.get('c', None)

    if key is None or key not in key_data:
        return render_template('error.html.jinja2', **params)        

    params.update({
        "next_page": url_for("survey_begin", c=key),
        "participant": key_data[key]['participant'],
        "npages": key_data[key]['npages']
    })

    return render_template('instructions.html.jinja2', **params)


@app.route('/start_survey')
def survey_begin():
    """Base url start the survey for user with key c"""
    c = request.args.get('c')
    params = dict(DEFAULT_PARAMS)
    post_links = []

    sub = subreddits[key_data[c]['index']]

    for id, data in post_link_data[sub].items():
        num = base_repr(int(id), 36)
        link = "https://reddit.com/r/" + sub + "/comments/" + num
        post_links.append((link, data))

    params.update({
        "c": c,
        "subreddit": subreddits[key_data[c]['index']],
        "id": key_data[c]['index'],
        "nmore": key_data[c]['npages'],
        "percent": 0,
        "post_links": post_links
    })
    return render_template('poll.html.jinja2', **params)


@app.route('/poll/<int:id>')
def poll(id):
    """The polling storage method for user with key c and for sequence id """
    params = dict(DEFAULT_PARAMS)
    
    key = request.args.get('c')
    allparams = request.args.items()
    subreddit = subreddits[id]

    for param in allparams:
        if param[0] == 'c' or param[0] == 'subreddit':
            continue
        else:
            query_db("insert into link_value values(?,?,?,?)",
                     [key, param[0], param[1], datetime.utcnow()])

    if id + 1 >= key_data[key]['npages'] + key_data[key]['index']:
        params.update({
            "participant": key_data[key]['participant']
        })
        return render_template('finish.html.jinja2', **params)
    
    else:
        sub = subreddits[id + 1]
        post_links = []
        for num, data in post_link_data[sub].items():
            num = base_repr(int(num), 36)
            link = "https://reddit.com/r/" + sub + "/comments/" + num
            post_links.append((link, data))

        params.update({
            "c": key,
            "subreddit": subreddits[id + 1],
            "id": id + 1,
            "nmore": key_data[key]['npages'] - (id - key_data[key]['index'] + 1),
            "percent": float(id - key_data[key]['index'] + 1) / key_data[key]['npages'] * 100,
            "post_links": post_links
        })
        return render_template('poll.html.jinja2', **params)


if __name__ == "__main__":
    app.run(debug=True)
