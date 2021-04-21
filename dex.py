species = {
        "Crockodyle":{"atk":100,"dfn":100,"spd":100,"spa":100,"spe":100,"types":["fire"]},
        "Puncher":{"atk":150,"dfn":120,"spd":80,"spa":60,"spe":85,"types":["fighting"]},
        "Aggrobull":{"atk":150,"dfn":100,"spd":100,"spa":105,"spe":140,"types":["dragon"]},
        "Serpyre":{"atk":130,"dfn":80,"spa":130,"spd":80,"spe":120,"types":["fire"]},

}

typekey = {"normal":0,"fighting":1,"flying":2,"rock":3,"steel":4,"dragon":5,"fire":6,"water":7,"grass":8,"psychic":9,"ghost":10,"dark":11}
typematchup = [[ 1, 1, 1,.5,.5, 1, 1, 1, 1, 1, 0, 1], #normal #offensive type THEN defensive type order..
               [ 2, 1,.5, 2, 2, 1, 1, 1, 1,.5, 0, 2], #fighting
               [ 1, 2, 1,.5,.5, 1, 1, 1, 2, 1, 1, 1], #flying
               [ 1,.5, 2, 1,.5, 1, 2, 1, 1, 1, 1, 1], #rock
               [ 1, 1, 1, 2,.5, 1,.5,.5, 1, 1, 1, 1], #steel
               [ 1, 1, 1, 1,.5, 2, 1, 1, 1, 1, 1, 1], #dragon
               [ 1, 1, 1,.5, 2,.5,.5,.5, 2, 1, 2, 2], #fire
               [ 1, 1, 1, 2, 1,.5, 2,.5,.5, 1, 1, 1], #water
               [ 1, 1,.5, 2,.5,.5,.5, 2,.5, 1, 1, 1], #grass
               [ 1, 2, 1, 1,.5, 1, 1, 1, 1,.5, 1, 0], #psychic
               [ 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2,.5], #ghost
               [ 1,.5, 1, 1, 1, 1, 1, 1, 1, 2, 2,.5]] #dark

def damage_dealing_move(user,target,isSpecial,movetype,movepower,movename):
    user = user.get_activemon()
    target = target.get_activemon()
    dmgmod = user.damage_calc_inflict()
    if not (user and target):
        print("user or target is KOd so damaging move failed")
        return
    user.side.room.log(user.get_name()+" used "+movename+"!")
    typeAdv = 1
    for x in target.types:
        typeAdv *= typematchup[typekey[movetype]][typekey[x]]
    if typeAdv == 0:
        user.side.room.log("It had no effect!")
        return 0
    if typeAdv < 1:
        user.side.room.log("It's not very effective...")
    if typeAdv > 1:
        user.side.room.log("It's super effective!")
    typeAdv *= dmgmod
    if movetype in user.types:
        typeAdv *= 1.5
    if isSpecial:
        damage = max(int(user.spa*movepower*typeAdv/target.spd),1)
    else:
        damage = max(int(user.atk*movepower*typeAdv/target.dfn),1)
    user.side.room.log(target.get_name()+" took "+str(damage)+" percent!")
    target.took_direct_damage(damage)
    target.take_damage(damage)
    return damage

class Move:

    def __init__(self, usemove, movetype, prioritycallback = None):
        self.movetype = movetype
        self.usemove = usemove
        self.prioritycallback = prioritycallback

    def __call__(self,user,target):
        self.usemove(user,target)

    def adjust_priority(self,user):
        if self.prioritycallback:
            return self.prioritycallback(user)
        return 0

class Status:

    def __init__(self,mon,name):
        self.name = name
        self.mon = mon

    def get_str(self):
        return self.name

    def turnendcallback(self):
        pass

    def remove(self):
        self.mon.remove_status(self)

    def tookdirectdamagecallback(self):
        pass

    def abouttousemovecallback(self):
        return False # if it returns true, prevents them from using a move

    def prioritycallback(self):
        return 0 #add speed to user

    def switchedoutcallback(self):
        self.remove()

    def damagecalccallbackattacker(self):
        return 1

def construct_damaging_move(isSpecial,movetype,BP,name):
    return Move(lambda x, y: damage_dealing_move(x,y,isSpecial,movetype,BP,name),movetype)

def pilebunker(user,target):
    damage_dealing_move(user,target,False,"fighting",40,"pilebunker")

def pilebunker_PCB(user):
    mon = user.get_activemon()
    class FocusStatus(Status):
        def turnendcallback(self):
            self.remove()
        def tookdirectdamagecallback(self):
            class FlinchStatus(Status):
                def turnendcallback(self):
                    self.remove()
                def abouttousemovecallback(self):
                    self.mon.log(self.mon.get_name()+" flinched!")
                    return True
            self.mon.add_status(FlinchStatus(self.mon,"flinching"))
    mon.add_status(FocusStatus(mon,"focussing"))
    mon.log(mon.get_name()+" gets an evil glint in its eye")
    return -1000

def rampage(user,target):
    victim = target.get_activemon()
    damage_dealing_move(user,target,False,"dragon",38,"rampage")
    if victim.is_fainted():
        victim.log(user.get_activemon().get_name()+" is tired out from its rampage!")
        class RechargeStatus(Status):
            def __init__(self,mon):
                Status.__init__(self,mon,"recharging")
                self.turnUsed = False
            def turnendcallback(self):
                if self.turnUsed:
                    self.remove()
                else:
                    self.turnUsed = True
                    self.mon.side.awaitingmove = False
            def abouttousemovecallback(self):
                self.mon.log(self.mon.get_name()+" is recharging!")
                return True
        user.get_activemon().add_status(RechargeStatus(user.get_activemon()))

def retreat(user,target):
    user.log(user.get_activemon().get_name()+" used retreat!")
    if user.get_num_living() == 1:
        user.log("BUT THERE'S NOWHERE LEFT TO RUN")
        return
    user.activemon = None
    user.panicking = True
    user.await_move()

def pilotlight(user,target):
    dmg = damage_dealing_move(user,target,True,"fire",5,"pilot light")
    if dmg:
        user.log(user.get_activemon().get_name()+" is getting fired up!")
        class LitStatus(Status):
            def __init__(self,mon):
                Status.__init__(self,mon,"lit")
                self.turnUsed = False
            def is_move_fire(self):
                action = self.mon.side.action
                if not action[0]:
                    return False
                return moves[self.mon.moves[action[1]]].movetype == "fire"
            def prioritycallback(self):
                if self.is_move_fire():
                    return 1000
                return 0
            def endturncallback(self):
                if self.turnUsed:
                    self.remove()
                else:
                    self.turnUsed=True
            def damagecalccallbackattacker(self):
                if self.is_move_fire():
                    self.remove()
                    return 1.5
                return 1
        user.get_activemon().add_status(LitStatus(user.get_activemon()))

    

moves = {
        "facepunch": construct_damaging_move(False,"fighting",25,"facepunch"),
        "falcon punch": construct_damaging_move(False,"fire",20,"falcon punch"),
        "boulder toss": construct_damaging_move(False,"rock",22,"boulder toss"),
        "forbidden shadow assault": construct_damaging_move(False,"dark",20,"forbidden shadow assault"),
        "pilebunker": Move(pilebunker,"fighting",prioritycallback=pilebunker_PCB),
        "dragon fang": construct_damaging_move(False,"dragon",23,"dragon fang"),
        "rampage": Move(rampage,"dragon"),
        "fire breath": construct_damaging_move(True,"fire",24,"fire breath"),
        "skydive": construct_damaging_move(False,"flying",20,"skydive"),
        "smoldering jaws": construct_damaging_move(False,"fire",24,"smoldering jaws"),
        "retreat": Move(retreat,"normal"),
        "pilot light": Move(pilotlight,"fire"),
        }

