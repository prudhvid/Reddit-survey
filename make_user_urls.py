#!/usr/bin/env python2
# encoding: utf-8
"""
Make the user-url config json.
"""

from __future__ import division, print_function


import json
import random

SUBREDDIT_FILE = './final_subs.txt'

def random_string():
    n = 10

    lower = "abcdefghijklmnopqrstuvwxyz"
    digits = "0123456789"

    return "".join(random.choice(lower + digits) for _ in range(n))

def get_lines(tbs):

    with open(SUBREDDIT_FILE) as obj:
        lines = []
        for line in obj.readlines():
            if len(line) == 1:
                continue
            else:
                lines.append(line)
        
        
        print(len(lines))
        return lines
    #     # TOTAL_BUCKETS = len(lines)/10 + 1
    #     nper_bucket = len(lines) / tbs
    #     for i in range(tbs):
    #         poll_data[i] = []

    #     index = 0
    #     for line in lines:
    #             subreddit = line.split(' ')[0].split('/')[-1]
    #             poll_data[int(index/nper_bucket)].append(subreddit)
    #             index += 1

    # return poll_data

def main():

    poll_data = {}

    

    # Url format
    urlfmt = """
    https://cnerg.iitkgp.ac.in/p/subreddit-value/?c={}
        """.strip().format

    # Email format
    emailfmt = """
    Dear {user},
    Please fill the following survey
    {url}


    Regards
    --
    Parantapa Bhattacharya
    """.strip().format

    # Users
    users = """
       Rijula 
       Prudhvi
       Mosam
       Suman
       Chakradhari
       Bishnoi
       Asim
       Karthik
    """.split()

    lines = get_lines(len(users))

    

    # Generate the objects
    rows = {}
    index = 0 
    
    for user in users:
        key = random_string()
        url = urlfmt(key)

        rows[key] = {
            "participant": user,
            "url": url,
            "npages": int(len(lines)/len(users)) if index<len(users)-1
                 else len(lines)-(len(users)-1)*int(len(lines)/len(users)),
            "index": index*int(len(lines)/len(users))
        }
        index += 1
        

        print(emailfmt(user=user, url=url))


    # Dump the objects
    ofname = "user-reddit.json"
    with open(ofname, "w") as fobj:
        json.dump(rows, fobj)

if __name__ == '__main__':
    main()

