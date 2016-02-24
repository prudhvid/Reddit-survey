from flask import Flask, render_template, request, send_from_directory
import os
import sqlite3
from flask import g,url_for

from contextlib import closing

app = Flask(__name__,static_url_path="")

# poll_data = {
#    'question' : 'Which web framework do you use?',
#    'fields'   : ['Flask', 'Django', 'TurboGears', 'web2py', 'pylonsproject']
# }

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

SUBREDDIT_FILE = "./subreddits.txt"

DEFAULT_PARAMS = {
    "survey": {
        "title": "Categorizing Reddit Subreddits",
        "description": (
            "Survey on categorizing post-based/comment-based subreddits"
            "in Reddit."),
    }
}

poll_data = []


with open(SUBREDDIT_FILE) as obj:
    lines = obj.readlines()
    for line in lines:
        if len(line) == 1:
            continue
        else:
            subreddit = line.split(' ')[0].split('/')[-1]
            poll_data.append(subreddit)



def connect_db():
    return sqlite3.connect(DATABASE)

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    g.db.commit()
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv



@app.route('/components/<path:path>')
def send_js(path):
    return send_from_directory('bower_components', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/')
def root():
    # return render_template('instructions.html.jinja2', data=poll_data[0], id=0, roll=roll)
    params=dict(DEFAULT_PARAMS)
    params.update({
        "next_page": url_for("login")
    })
    
    return render_template('instructions.html.jinja2',**params)

@app.route('/user')
def login():
    params=dict(DEFAULT_PARAMS)
    return render_template('user.html.jinja2', data=poll_data[0], id=0,**params)


@app.route('/adduser', methods = ['POST','GET'] )
def adduser():
    name, roll = request.form['name'],request.form['roll']
    print name, roll
    res = query_db("insert into user values(?,?)",[roll,name])
    if res is None:
        return 'failed'
    else:
        params=dict(DEFAULT_PARAMS)
        params.update({
            "roll" : roll,
            "data" : poll_data[0],
            "id"   : 0
            })
        return render_template('poll.html.jinja2',**params)




@app.route('/poll/<int:id>')
def poll(id):

    params=dict(DEFAULT_PARAMS)
    
    vote = request.args.get('field')
    roll = request.args.get('roll')
    subreddit = request.args.get('subreddit')

    query_db("insert into survey values(?,?,?)",[roll,subreddit,vote])

    
    if id+1 >= len(poll_data):
        return render_template('finish.html.jinja2',**params)
    else:
        params.update({
            "roll" : roll,
            "data" : poll_data[id+1],
            "id"   : id+1
            })
        return render_template('poll.html.jinja2', **params)

@app.route('/results')
def show_results():
    votes = {}
    for f in poll_data['fields']:
        votes[f] = 0

    f  = open(filename, 'r')
    for line in f:
        vote = line.rstrip("\n")
        votes[vote] += 1

    return render_template('results.html', data=poll_data, votes=votes)



if __name__ == "__main__":
    app.run(debug=True)

