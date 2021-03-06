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
        self.atkboosts = 0
        self.spaboosts = 0
        self.dfnboosts = 0
        self.spdboosts = 0
        self.speboosts = 0
        self.types = self.species["types"]
        self.health = 400
        self.moves = json["moves"]
        for move in self.moves:
            if move not in moves:
                print(move)
                1/0
        self.side = side
        self.status = [] 
        self.prioritycallbacks = []
        self.seen = False

    def get_atk(self):
        return self.get_stat(self.atk,self.atkboosts)
    def get_dfn(self):
        return self.get_stat(self.dfn,self.dfnboosts)
    def get_spa(self):
        return self.get_stat(self.spa,self.spaboosts)
    def get_spd(self):
        return self.get_stat(self.spd,self.spdboosts)
    def get_spe(self):
        return self.get_stat(self.spe,self.speboosts)

    def get_stat(self,stat,boosts):
        if boosts > 0:
            return stat * (1+(boosts/2))
        return stat / (1+(boosts/-2))

    def get_all_status_str(self):
        status = [i.get_str() for i in self.status[::-1]]
        if self.atkboosts>0:
            status.append("attack +"+str(self.atkboosts))
        elif self.atkboosts<0:
            status.append("attack "+str(self.atkboosts))
        if self.spaboosts>0:
            status.append("special attack +"+str(self.spaboosts))
        elif self.spaboosts<0:
            status.append("special attack "+str(self.spaboosts))
        if self.dfnboosts>0:
            status.append("defense +"+str(self.dfnboosts))
        elif self.dfnboosts<0:
            status.append("defense "+str(self.dfnboosts))
        if self.spdboosts>0:
            status.append("special defense +"+str(self.spdboosts))
        elif self.spdboosts<0:
            status.append("special defense "+str(self.spdboosts))
        if self.speboosts>0:
            status.append("speed +"+str(self.speboosts))
        elif self.speboosts<0:
            status.append("speed "+str(self.speboosts))
        return status

    def is_fainted(self):
        return self.health > 0

    def add_status(self,status):
        self.status.insert(0,status)

    def remove_status(self,status):
        if status in self.status:
            self.status.remove(status)

    def get_name(self):
        return self.nick+"("+self.speciesname+")"

    def get_moves(self):
        return self.moves

    def take_damage(self,damage):
        self.health -= damage
        if not self.is_fainted():
            self.side.knockout()

    def took_direct_damage(self,dmg):
        tookdirectdamagecallbacks = [i for i in self.status]
        for callback in tookdirectdamagecallbacks:
            callback.tookdirectdamagecallback()

    def turn_ended(self):
        turnendcallbacks = [i for i in self.status]
        for callback in turnendcallbacks:
            callback.turnendcallback()

    def pre_turn_ended(self):
        for callback in [i for i in self.status]:
            callback.preturnendcallback()

    def fainted(self):
        callbacks = [i for i in self.status]
        for callback in callbacks:
            callback.knockedoutcallback()


    def switched_out(self):
        for callback in [i for i in self.status]:
            callback.switchedoutcallback()
        self.atkboosts = 0
        self.spaboosts = 0
        self.dfnboosts = 0
        self.spdboosts = 0
        self.speboosts = 0

    def switched_in(self):
        self.seen = True

    def log(self,info):
        self.side.log(info)

    def damage_calc_inflict(self):
        out = 1
        for callback in [i for i in self.status]:
            out *= callback.damagecalccallbackattacker()
        return out

    def damage_calc_receive(self):
        out = 1
        for callback in [i for i in self.status]:
            out *= callback.damagecalccallbackdefender()
        return out

    def is_move_valid(self,isMove,choice):
        for status in self.status:
            if not status.movevalidcallback(isMove,choice):
                return False
        return True

class Side():

    def __init__(self):
        """creates new side sans team"""
        self.hasteam = False
        self.awaitingmove = True
        self.awaitingrevenge = False
        self.panicking = False
        self.action = None
        self.activemon = None
        self.team = None
        self.room = None
        self.fieldeffects = []
        self.otherside = None

    def add_effect(self,effect):
        self.fieldeffects.append(effect)

    def remove_effect(self,effect):
        if effect in self.fieldeffects:
            self.fieldeffects.remove(effect)

    def get_num_living(self):
        tot = 0
        for mon in self.team:
            if mon.is_fainted():
                tot+=1
        return tot

    def get_activemon(self):
        if not self.hasteam:
            return None
        if self.activemon == None:
            return None
        return self.team[self.activemon]

    def knockout(self):
        self.room.log(self.get_activemon().get_name()+" fainted!")
        self.get_activemon().fainted()
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
        self.get_activemon().seen = True

    def assign_room(self,room):
        self.room = room

    def await_move(self):
        self.awaitingmove = True

    def get_name_active(self):
        if self.get_activemon() == None:
            return None
        return self.get_activemon().get_name()

    def get_status_active(self):
        out = []
        for i in self.fieldeffects:
            if i.get_visible():
                out.append(i.get_str())
        if self.get_activemon() == None:
            return out
        return out + self.get_activemon().get_all_status_str()

    def get_health_active(self):
        if self.get_activemon() == None:
            return None
        return self.get_activemon().health

    def get_moves_active(self):
        if self.get_activemon() == None:
            return None
        return self.get_activemon().get_moves()

    def get_seen_mons(self):
        if not self.team:
            return None
        out = []
        for mon in self.team:
            if mon.seen:
                out.append(mon.get_name())
        return out

    def get_seen_healths(self):
        if not self.team:
            return None
        out = []
        for mon in self.team:
            if mon.seen:
                out.append(mon.health)
        return out

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
        for callback in [i for i in self.get_activemon().status]:
            movespeedmod += callback.prioritycallback()
        self.get_activemon().prioritycallbacks = []
        return self.get_activemon().get_spe() + movespeedmod

    def execute_action(self,targetside):
        if self.get_activemon() == None:
            return
        abouttousemovecallbacks = [i for i in self.get_activemon().status]
        canusemove = True
        for callback in abouttousemovecallbacks:
            canusemove = canusemove and (not callback.abouttousemovecallback())
        if not canusemove:
            return
        if self.action[0]:
            movefun = moves[self.get_activemon().moves[self.action[1]]]
            movefun(self,targetside)
        else:
            self.switchin(self.action[1])

    def switched_out(self):
        for callback in [i for i in self.fieldeffects]:
            callback.switchedoutcallback()
        if self.get_activemon():
            self.get_activemon().switched_out()


    def switchin(self,target):
        if self.get_activemon():
            self.switched_out()
        self.activemon = target
        self.log(self.get_activemon().get_name()+" switches in!")
        for callback in [i for i in self.fieldeffects]:
            callback.switchedincallback()
        if self.get_activemon():
            self.get_activemon().switched_in()

    def revengein(self):
        self.awaitingrevenge = False
        self.switchin(self.action[1])

    def panicin(self):
        self.panicking = False
        self.switchin(self.action[1])

    def has_active_mon(self):
        return self.get_activemon() != None

    def turn_ended(self):
        for callback in [i for i in self.fieldeffects]:
            callback.turnendcallback()
        self.get_activemon().turn_ended()

    def pre_turn_end(self):
        for callback in [i for i in self.fieldeffects]:
            callback.preturnendcallback()
        if self.get_activemon():
            self.get_activemon().pre_turn_ended()

    def is_move_valid(self,isMove,choice):
        if (self.awaitingrevenge or self.panicking) and isMove:
            print("cannot make move while awaiting revenge or panicking")
            return False
        if (not isMove) and (not self.team[choice].is_fainted()):
            print("cannot switch in a fainted mon")
            return False
        if (not isMove) and (choice == self.activemon):
            print("cannot switch in currently active mon")
            return False
        if self.get_activemon():
            if not self.get_activemon().is_move_valid(isMove,choice):
                print("status restricting options")
                return False
        for effect in self.fieldeffects:
            if not effect.movevalidcallback(isMove,choice):
                print("field effect restricting options")
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
        self.p1.otherside = self.p2
        self.p2.otherside = self.p1
        self.winner = None
        self.past = []
        self.postpanic = None

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
        if self.p1.panicking:
            self.p1.panicin()
            self.postpanic()
            return
        elif self.p2.panicking:
            self.p2.panicin()
            self.postpanic()
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
            if self.p1.panicking:
                self.postpanic = lambda: self.action_then_finish(self.p2,self.p1)
                return
            self.p2.execute_action(self.p1)
            if self.p2.panicking:
                self.postpanic = lambda: self.finish_turn()
                return
        else:
            self.p2.execute_action(self.p1)
            if self.p2.panicking:
                self.postpanic = lambda: self.action_then_finish(self.p1,self.p2)
                return
            self.p1.execute_action(self.p2)
            if self.p1.panicking:
                self.postpanic = lambda: self.finish_turn()
                return

        self.finish_turn()

    def action_then_finish(self,actor,target):
        actor.execute_action(target)
        if actor.panicking:
            self.postpanic = lambda: self.finish_turn()
            return
        self.finish_turn()

    def pre_revenge_turn_end(self):
        self.p1.pre_turn_end()
        self.p2.pre_turn_end()

    def finish_turn(self):
        self.pre_revenge_turn_end()
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

@app.route('/', methods = ['POST'])
def result():
    received = request.get_json(force=True)
    reqtype = received["type"]
    if received["type"] == "makeroom":
        rooms.append(Room())
        return "{}"
    if received["type"] == "getrooms":
        thing = {"numrooms":len(rooms)}
        response = jsonify(thing)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    if reqtype == "getinfo":
        return getinfo(received)
    roomnum = received["room"]
    side=rooms[roomnum].get_side(received["side"])
    if received["type"] == "team":
        side.load_team(received["mons"])
    if received["type"] == "move":
        side.queue_action(True,received["move"])
    if received["type"] == "swap":
        side.queue_action(False,received["mon"])
    return "{}"

def getinfo(received):
    roomnum = received["room"]
    if roomnum >= len(rooms):
        return "{}"
    p1side = rooms[roomnum].get_side(False)
    p2side = rooms[roomnum].get_side(True)
    thing = {"fightactive":rooms[roomnum].fight_active(),"p1mon":p1side.get_name_active(),"p2mon":p2side.get_name_active(),"p1health":p1side.get_health_active(),"p2health":p2side.get_health_active(),"p1moves":p1side.get_moves_active(),"p2moves":p2side.get_moves_active(),"p1switches":p1side.get_switches(),"p2switches":p2side.get_switches(),"winner":rooms[roomnum].winner,"log":rooms[roomnum].past,"p1status":p1side.get_status_active(),"p2status":p2side.get_status_active(),"p1healths":p1side.get_seen_healths(),"p2healths":p2side.get_seen_healths(),"p1mons":p1side.get_seen_mons(),"p2mons":p2side.get_seen_mons()}
    response = jsonify(thing)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
