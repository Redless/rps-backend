from flask import Flask, jsonify, request
from multiprocessing import Manager
from flask_cors import CORS

app = Flask(__name__, static_folder='app', static_url_path="/app")

CORS(app)

leader = Manager()
p1moves = leader.list()
p2moves = leader.list()
movereceived = leader.list()
movereceived.append(False)
movereceived.append(False)
score = leader.list()
score.append(0)
score.append(0)

rpsdict = {"rock":0,"paper":1,"scissors":2}

def updatescore():
    if len(p1moves) != len(p2moves):
        1/0
    p1move = rpsdict[p1moves[-1]]
    p2move = rpsdict[p2moves[-1]]
    movereceived[0]=False
    movereceived[1]=False
    if p1move == p2move:
        return
    if ((p1move+1)%3) == p2move:
        score[1]+=1
        return
    if ((p2move+1)%3) == p1move:
        score[0]+=1
        return
    1/0

    

@app.route('/', methods = ['POST'])
def result():
    received = request.get_json(force=True)
    side = received["side"]
    move = received["move"]
    if not side:
        if not movereceived[side]:
            movereceived[side] = True
            p1moves.append(move)

    else:
        if not movereceived[side]:
            movereceived[side] = True
            p2moves.append(move)
    if movereceived[0] and movereceived[1]:
        updatescore()

    return ": )"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    response = jsonify({"p1score":score[0],"p2score":score[1],"p1moves":list(p1moves),"p2moves":list(p2moves)})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
