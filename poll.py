import flask
from flask import Flask, render_template, request, send_from_directory
import os
import sqlite3
from flask import g,url_for
from contextlib import closing
import json
from numpy import base_repr

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

SUBREDDIT_FILE = "./final_subs.txt"

JSONFILE = './user-reddit.json'

POSTS_LINK_FILE = './final_sub_posts.json'

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



with open(SUBREDDIT_FILE) as obj:
    lines = []
    for line in obj.readlines():
        if len(line) == 1:
            continue
        else:
            line = line[:-1]
            lines.append(line)



def readJson():
    global key_data
    with open(JSONFILE) as jf:
        key_data = json.load(jf)

readJson()

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




# Static serve files

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

@app.route('/url')
def url_root():
    params=dict(DEFAULT_PARAMS)
    key = request.args.get('c')

    params.update({
        "next_page": url_for("survey_begin",c=key),
        "participant": key_data[key]['participant'],
        "npages": key_data[key]['npages']
    })

    return render_template('instructions.html.jinja2',**params)

@app.route('/start_survey')
def survey_begin():
    c=request.args.get('c')
    params=dict(DEFAULT_PARAMS)
    post_links = []
    
    sub = lines[key_data[c]['index']]

    for id in post_link_data[sub]:
        num = base_repr(int(id), 36)
        link = "https://reddit.com/r/"+sub+"/comments/"+num
        post_links.append(link)

    params.update({
        "c" : c,
        "data" : lines[key_data[c]['index']],
        "id"   : key_data[c]['index'],
        "nmore": key_data[c]['npages'],
        "percent":0,
        "post_links":post_links
        })
    return render_template('poll.html.jinja2', **params)
    


@app.route('/user')
def login():
    params=dict(DEFAULT_PARAMS)
    return render_template('user.html.jinja2', data=poll_data[0], id=0,**params)


@app.route('/adduser', methods = ['POST','GET'] )
def adduser():
    global prev_poll_no
    name, roll = request.form['name'],request.form['roll']
    print name, roll
    res = query_db("insert into user values(?,?)",[roll,name])
    if res is None:
        return 'failed'
    else:
        params=dict(DEFAULT_PARAMS)
        prev_poll_no = (prev_poll_no+1)%TOTAL_BUCKETS
        params.update({
            "roll": roll,
            "data": poll_data[prev_poll_no][0],
            "poll_no": prev_poll_no ,
            "id"   : 0
            })
        return render_template('poll.html.jinja2',**params) 



@app.route('/poll/<int:id>')
def poll(id):

    params=dict(DEFAULT_PARAMS)
    
    vote = request.args.get('field')
    key = request.args.get('c')
    subreddit = lines[id]

    query_db("insert into survey values(?,?,?)",[key,subreddit,vote])

    
    if id+1 >= key_data[key]['npages']+key_data[key]['index']:
        params.update({
            "participant":key_data[key]['participant']
            })
        return render_template('finish.html.jinja2',**params)
    else:
        
        sub = lines[id+1]
        post_links = []
        for id in post_link_data[sub]:
            num = base_repr(int(id), 36)
            link = "https://reddit.com/r/"+sub+"/comments/"+num
            post_links.append(link)


        params.update({
            "c" : key,
            "data" : lines[id+1],
            "id"   : id+1,
            "nmore": key_data[key]['npages']-(id-key_data[key]['index']+1),
            "percent":float(id-key_data[key]['index']+1)/key_data[key]['npages']*100,
            "post_links": post_links
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

