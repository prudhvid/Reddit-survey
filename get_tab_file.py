import sqlite3
import json

con = sqlite3.connect('./data.sqlite3')

cur = con.cursor()

cur.execute('select * from link_value')


with open('./final_post_data.json') as fobj:
    data = json.load(fobj)
    
with open('./eval.txt','w') as fobj:
    while True:
      
        row = cur.fetchone()
        
        if row == None:
            break
        

        user,id,value,time = row[0],row[1],row[2],row[3]

        iid = int(id,36)

        for sub,links in data.iteritems():
            if str(iid) in links:
                # print sub, "https://reddit.com/r/" + sub + "/comments/" + id, value
                url = "https://reddit.com/r/" + sub + "/comments/" + id
                fobj.write(id+"\t"+url+"\t"+value+"\t"+time+"\n")