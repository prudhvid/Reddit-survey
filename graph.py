import plotly.plotly as py
import plotly.graph_objs as go
import json

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


alive_subs_nusers = []
dead_subs_nusers = []

alive_data = []
dead_data = []
for sub, npc in data.iteritems():
    if sub in alive:
        alive_subs_nusers.append(uu[sub])
        alive_data.append(float(npc[0]-npc[1])/(npc[0]+npc[1]))
    if sub in dead:
        dead_subs_nusers.append(uu[sub])
        dead_data.append(float(npc[0]-npc[1])/(npc[0]+npc[1]))


# matplotlib.pyplot.scatter(alive_data,alive_subs)
# matplotlib.pyplot.scatter(alive_data,alive_subs)

# matplotlib.pyplot.show()


# trace0 = go.Scatter(
#     y = alive_subs_nusers,
#     x = alive_data,
#     mode = 'markers',
#     name = 'alive'
# )
# trace1 = go.Scatter(
#     y = dead_subs_nusers,
#     x = dead_data,
#     mode = 'markers',
#     name = 'dead'
# )

trace0 = go.Histogram(
    y = alive_subs_nusers,
    x = alive_data,
    opacity = 0.75,
    name = 'alive'
)
trace1 = go.Scatter(
    y = dead_subs_nusers,
    x = dead_data,
    opacity = 0.75,
    name = 'dead'
)


layout = go.Layout(
    yaxis=dict(
        type='log',
        autorange=True,
        title='#unique users',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    ),

    xaxis=dict(
        title='p-c/p+c',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    ),
    barmode = 'overlay'
)


# py.sign_in('dharmana.prudhvi', 'r4t7u4rkbw')
gdata = [trace0, trace1]
fig = go.Figure(data=gdata, layout=layout)
py.plot(fig, filename='overlaid-histogram')