import json
from sklearn import svm
from sklearn import tree
from sklearn.cross_validation import train_test_split
from sklearn import cross_validation
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn import preprocessing

data = {}

with open('./eval.txt') as fobj:
    for line in fobj.readlines():
        cols = line.split()
        sub =  cols[1].split('/')[4]
        if not sub in data:
            data[sub] = [0, 0]
        
        if cols[2] == 'p':
            data[sub][0] += 1
        elif cols[2] == 'c':
            data[sub][1] += 1


with open('./final_subs.txt') as fobj:
    subs = fobj.read().split()
    alive = set(subs[:200])
    dead = set(subs[200:])

    


with open('./unique_subs.json') as fobj:
    uu = json.load(fobj)

with open('./data/unique_users.json') as fobj:
    unique_users_fd = json.load(fobj)

with open('./data/nposts.json') as fobj:
    nposts_fd = json.load(fobj)

with open('./data/ncomments_perpost.json') as fobj:
    ncomments_perpost_fd = json.load(fobj)

with open('./data/nvotes_perpost.json') as fobj:
    nvotes_perpost_fd = json.load(fobj)



pc_data_fd = {}

X = []
Y = []



for sub, npc in data.iteritems():
    if sub in alive or sub in dead:
        x = []
        x.append(float(npc[0]-npc[1])/(npc[0]+npc[1]))
        if sub in unique_users_fd and sub in ncomments_perpost_fd:
            x.append(unique_users_fd[sub]['mean'])
            x.append(unique_users_fd[sub]['sd'])
            x.append(unique_users_fd[sub]['peak'])
            x.append(nposts_fd[sub]['mean'])
            x.append(nposts_fd[sub]['sd'])
            x.append(nposts_fd[sub]['peak'])
            x.append(ncomments_perpost_fd[sub]['mean'])
            x.append(ncomments_perpost_fd[sub]['sd'])
            x.append(ncomments_perpost_fd[sub]['peak'])
            x.append(nvotes_perpost_fd[sub]['mean'])
            x.append(nvotes_perpost_fd[sub]['sd'])
            x.append(nvotes_perpost_fd[sub]['peak'])

            X.append(x)
            Y.append( 1 if sub in alive else 0 )
        




X = preprocessing.normalize(X, norm='l2')
# print X.shape

X_train, X_test, y_train, y_test = train_test_split(
     X, Y, test_size=0.20, random_state=42)



clf = svm.SVC(kernel = 'linear')
# clf = tree.DecisionTreeClassifier(max_depth=3)
# clf = AdaBoostClassifier()




scores = cross_validation.cross_val_score(
    clf, X, Y, n_jobs = -1, cv=5)
print scores


print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

# print clf.predict(X[351])