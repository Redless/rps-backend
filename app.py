from flask import Flask, jsonify, request
from flask_cors import CORS
from dex import moves, species

app = Flask(__name__, static_folder='app', static_url_path="/app")

CORS(app)


class Mon():

    def __init__(self,json,side):
        self.speciesname = json["species"]
        self.species = species[json["species"]]
        self.nick = json["nick"]
        self.atk = self.species["atk"] + json["atk"]
        self.spa = self.species["spa"] + json["spa"]
        self.dfn = self.species["dfn"] + json["dfn"]
        self.spd = self.species["spd"] + json["spd"]
        self.spe = self.species["spe"]
        self.types = self.species["types"]
        self.health = 100
        self.moves = json["moves"]
        self.side = side
        self.took_direct_damage_this_turn = False
        self.status = set()
        self.turnendcallbacks = []
        self.tookdirectdamagecallbacks = []
        self.abouttousemovecallbacks = []
        self.prioritycallbacks = []

    def is_fainted(self):
        return self.health > 0

    def get_name(self):
        return self.nick+"("+self.speciesname+")"

    def get_moves(self):
        return self.moves

    def take_damage(self,damage):
        self.health -= damage
        if not self.is_fainted():
            self.side.knockout()

    def took_direct_damage(self,dmg):
        for callback in self.tookdirectdamagecallbacks:
            callback(dmg)
        self.tookdirectdamagecallbacks = []

    def turn_ended(self):
        nextturnendcallbacks = []
        for callback in self.turnendcallbacks:
            callback(self,nextturnendcallbacks)
        self.took_direct_damage_this_turn = False
        self.turnendcallbacks = nextturnendcallbacks


    def took_attack_this_turn(self):
        return self.took_direct_damage_this_turn

    def switched_out(self):
        self.took_direct_damage_this_turn = False

    def switched_in(self):
        pass

    def log(self,info):
        self.side.log(info)

class Side():

    def __init__(self):
        """creates new side sans team"""
        self.hasteam = False
        self.awaitingmove = True
        self.awaitingrevenge = False
        self.action = None
        self.activemon = None
        self.team = None
        self.room = None

    def get_activemon(self):
        if not self.hasteam:
            return None
        if self.activemon == None:
            return None
        return self.team[self.activemon]

    def knockout(self):
        self.room.log(self.get_activemon().get_name()+" fainted!")
        self.activemon = None
        if self.whole_team_KO():
            self.room.finishgame(self)
        self.awaitingrevenge = True

    def whole_team_KO(self):
        for mon in self.team:
            if mon.is_fainted():
                return False
        return True

    def load_team(self,teamjson):
        if self.hasteam:
            return
        team = []
        for mon in teamjson:
            team.append(Mon(mon,self))
        self.activemon = 0
        self.team = team
        self.hasteam = True
        if self.room.fight_active():
            self.room.get_side(True).await_move()
            self.room.get_side(False).await_move()
            self.room.log("let the games begin!")
            self.room.log("turn: 1")

    def assign_room(self,room):
        self.room = room

    def await_move(self):
        self.awaitingmove = True

    def get_name_active(self):
        if self.get_activemon() == None:
            return None
        return self.get_activemon().get_name()

    def get_status_active(self):
        if self.get_activemon() == None:
            return []
        return list(self.get_activemon().status)

    def get_health_active(self):
        if self.get_activemon() == None:
            return None
        return self.get_activemon().health

    def get_moves_active(self):
        if self.get_activemon() == None:
            return None
        return self.get_activemon().get_moves()

    def get_switches(self):
        if not self.team:
            return None
        return [mon.get_name() for mon in self.team]

    def has_team(self):
        return self.hasteam

    def queue_action(self,isMove,choice):
        if self.awaitingmove:
            if not self.is_move_valid(isMove,choice):
                return
            self.awaitingmove = False
            self.action = (isMove,choice)
            if self.get_activemon():
                if isMove:
                    self.get_activemon().prioritycallbacks.append(lambda x: moves[self.get_activemon().moves[choice]].adjust_priority(self))
                else:
                    self.get_activemon().prioritycallbacks.append(lambda x: 3000)
            self.room.execute_turn()

    def get_priority(self):
        movespeedmod = 0
        for callback in self.get_activemon().prioritycallbacks:
            movespeedmod += callback(self.get_activemon())
        self.get_activemon().prioritycallbacks = []
        return self.get_activemon().spe + movespeedmod

    def execute_action(self,targetside):
        if self.get_activemon() == None:
            return
        for callback in self.get_activemon().abouttousemovecallbacks:
            if callback():
                self.get_activemon().abouttousemovecallbacks = []
                return
        self.get_activemon().abouttousemovecallbacks = []
        if self.action[0]:
            movefun = moves[self.get_activemon().moves[self.action[1]]]
            movefun(self,targetside)
        else:
            self.switchin(self.action[1])


    def switchin(self,target):
        if self.get_activemon():
            self.get_activemon().switched_out()
        self.activemon = target
        self.get_activemon().switched_in()
        self.log(self.get_activemon().get_name()+" switches in!")

    def revengein(self):
        self.awaitingrevenge = False
        self.switchin(self.action[1])

    def has_active_mon(self):
        return self.get_activemon() != None

    def turn_ended(self):
        self.get_activemon().turn_ended()

    def is_move_valid(self,isMove,choice):
        if self.awaitingrevenge and isMove:
            print("cannot make move while awaiting revenge")
            return False
        if (not isMove) and (not self.team[choice].is_fainted()):
            print("cannot switch in a fainted mon")
            return False
        if (not isMove) and (choice == self.activemon):
            print("cannot switch in currently active mon")
            return False
        return True

    def log(self,info):
        self.room.log(info)

class Room():

    def __init__(self):
        """new room"""
        self.turncount = 1
        self.onrevenge = False
        self.p1 = Side()
        self.p2 = Side()
        self.p1.assign_room(self)
        self.p2.assign_room(self)
        self.winner = None
        self.past = []

    def log(self,info):
        self.past.insert(0,info)

    def finishgame(self,loser):
        if self.winner:
            return
        if loser == self.p1:
            self.winner = "p2"
        if loser == self.p2:
            self.winner = "p1"

    def get_side(self,isp1):
        return self.p2 if isp1 else self.p1

    def fight_active(self):
        return self.p1.has_team() and self.p2.has_team()

    def execute_turn(self):
        if (self.p1.awaitingmove) or (self.p2.awaitingmove):
            return
        if self.onrevenge:
            if self.p1.awaitingrevenge:
                self.p1.revengein()
            if self.p2.awaitingrevenge:
                self.p2.revengein()
            self.onrevenge = False
            self.check_for_revenge()
            return
        p1prio = self.p1.get_priority()
        p2prio = self.p2.get_priority()
        if (self.turncount%2):
            p1prio += .5
        else:
            p2prio += .5
        if p1prio > p2prio:
            self.p1.execute_action(self.p2)
            self.p2.execute_action(self.p1)
        else:
            self.p2.execute_action(self.p1)
            self.p1.execute_action(self.p2)

        self.check_for_revenge()

    def check_for_revenge(self):
        if self.winner:
            return
        if self.p2.awaitingrevenge:
            self.onrevenge = True
            self.p2.await_move()
        if self.p1.awaitingrevenge:
            self.onrevenge = True
            self.p1.await_move()
        if not self.onrevenge:
            self.turncount += 1
            self.p1.await_move()
            self.p2.await_move()
            self.turn_ended()
            self.log("turn: "+str(self.turncount))

    def turn_ended(self):
        self.p1.turn_ended()
        self.p2.turn_ended()



rooms = []
rooms.append(Room())

@app.route('/', methods = ['POST'])
def result():
    received = request.get_json(force=True)
    side=rooms[0].get_side(received["side"])
    if received["type"] == "team":
        side.load_team(received["mons"])
    if received["type"] == "move":
        side.queue_action(True,received["move"])
    if received["type"] == "swap":
        side.queue_action(False,received["mon"])
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
    thing = {"fightactive":rooms[0].fight_active(),"p1mon":p1side.get_name_active(),"p2mon":p2side.get_name_active(),"p1health":p1side.get_health_active(),"p2health":p2side.get_health_active(),"p1moves":p1side.get_moves_active(),"p2moves":p2side.get_moves_active(),"p1switches":p1side.get_switches(),"p2switches":p2side.get_switches(),"winner":rooms[0].winner,"log":rooms[0].past,"p1status":p1side.get_status_active(),"p2status":p2side.get_status_active()}
    #print("sending",thing)
    response = jsonify(thing)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
