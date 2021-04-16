from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__, static_folder='app', static_url_path="/app")

CORS(app)

p1movereceived=False
p2movereceived=False
p2moves = []
p1moves = []
p1score = 0
p2score = 0

rpsdict = {"rock":0,"paper":1,"scissors":2}

def updatescore():
    global p1score
    global p2score
    global p1movereceived
    global p2movereceived
    if len(p1moves) != len(p2moves):
        1/0
    p1move = rpsdict[p1moves[-1]]
    p2move = rpsdict[p2moves[-1]]
    p2movereceived=False
    p1movereceived=False
    if p1move == p2move:
        return
    if ((p1move+1)%3) == p2move:
        p2score+=1
        return
    if ((p2move+1)%3) == p1move:
        p1score+=1
        return
    1/0

    

@app.route('/', methods = ['POST'])
def result():
    received = request.get_json(force=True)
    side = received["side"]
    move = received["move"]
    process_new_move(side,move)
    return "{}"

def process_new_move(side,move):
    global p1movereceived
    global p2movereceived
    if not side:
        if not p1movereceived:
            p1movereceived = True
            p1moves.append(move)

    else:
        if not p2movereceived:
            p2movereceived = True
            p2moves.append(move)
    if p2movereceived and p1movereceived:
        updatescore()


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    response = jsonify({"p1score":p1score,"p2score":p2score,"p1moves":p1moves,"p2moves":p2moves})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
