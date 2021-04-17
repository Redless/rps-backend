from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__, static_folder='app', static_url_path="/app")

CORS(app)

species = {"Crockodyle":{"atk":100,"dfn":100,"spd":100,"spa":100,"spe":100,"types":["fire"]}}

class Mon():

    def __init__(self,json):
        self.speciesname = json["species"]
        self.species = species[json["species"]]
        self.nick = json["nick"]
        self.atk = self.species["atk"] + json["atk"]
        self.spa = self.species["spa"] + json["spa"]
        self.dfn = self.species["dfn"] + json["dfn"]
        self.spd = self.species["spd"] + json["spd"]
        self.spe = self.species["spe"]
        self.types = self.species["types"]
        self.currHP = 100
        self.moves = json["moves"]

    '''{"mons":[
        {"species":"Crockodyle","nick":"nicholas","atk":0,"spa":0,"dfn":0,"spd":0,"moves":["smack","bludgeon"]},
        {"species":"Crockodyle","nick":"dave","atk":0,"spa":0,"dfn":0,"spd":0,"moves":["smack","bludgeon"]},
        ]}'''

    def is_fainted(self):
        return self.currHP > 0

    def get_name(self):
        return self.nick+"("+self.speciesname+")"

class Side():

    def __init__(self):
        """creates new side sans team"""
        self.hasteam = False
        self.awaitingmove = False
        self.activemon = None
        self.team = None

    def load_team(self,teamjson):
        if self.hasteam:
            return
        team = []
        for mon in teamjson:
            team.append(Mon(mon))
        self.activemon = team[0]
        self.team = team
        self.hasteam = True

    def get_name_active(self):
        if not self.activemon:
            return None
        return self.activemon.get_name()

    def has_team(self):
        return self.hasteam

class Room():

    def __init__(self):
        """new room"""
        self.p1 = Side()
        self.p2 = Side()

    def get_side(self,isp1):
        return self.p2 if isp1 else self.p1

    def fight_active(self):
        return self.p1.has_team() and self.p2.has_team()


rooms = []
rooms.append(Room())

@app.route('/', methods = ['POST'])
def result():
    received = request.get_json(force=True)
    print(received)
    side=rooms[0].get_side(received["side"])
    side.load_team(received["mons"])
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
    p1side = rooms[0].get_side(False)
    p2side = rooms[0].get_side(True)
    response = jsonify({"fightactive":rooms[0].fight_active(),"p1mon":p1side.get_name_active(),"p2mon":p2side.get_name_active(),"p1health":100,"p2health":100,"p1moves":["smack","bludgeon"],"p2moves":["smack","bludgeon"],"p1switches":["no"],"p2switches":["yes"]})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
