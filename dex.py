species = {
        "Crockodyle":{"atk":100,"dfn":100,"spd":100,"spa":100,"spe":100,"types":["fire"]},
        "Puncher":{"atk":150,"dfn":120,"spd":80,"spa":60,"spe":85,"types":["fighting"]},
        "Aggrobull":{"atk":150,"dfn":100,"spd":100,"spa":105,"spe":140,"types":["dragon"]},
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

    def __init__(self, usemove, prioritycallback = None):
        self.usemove = usemove
        self.prioritycallback = prioritycallback

    def __call__(self,user,target):
        self.usemove(user,target)

    def adjust_priority(self,user):
        if self.prioritycallback:
            return self.prioritycallback(user)
        return 0

def construct_damaging_move(isSpecial,movetype,BP,name):
    return Move(lambda x, y: damage_dealing_move(x,y,isSpecial,movetype,BP,name))

def pilebunker(user,target):
    damage_dealing_move(user,target,False,"fighting",40,"pilebunker")

def pilebunker_PCB(user):
    mon = user.get_activemon()
    mon.log("PBPCB go")
    mon.status.add("focussing")
    def focus_flinch(whatever):
        mon.log("focus flinch")
        mon.log(str(mon.status))
        if not ("focussing" in mon.status):
            return
        mon.log("flinched by move")
        mon.status.add("flinch")
        def flinch():
            if "flinch" in mon.status:
                mon.status.remove("flinch")
                mon.log(mon.get_name()+" flinched!")
                return True
            return False
        mon.abouttousemovecallbacks.append(flinch)
    mon.tookdirectdamagecallbacks.append(focus_flinch)
    def helpme(x,y):
        mon.log("here goes nothing")
        mon.log(str(mon.status))
        if "focussing" in mon.status:
            mon.status.remove("focussing")
        mon.log(str(mon.status))
    mon.turnendcallbacks.append(helpme)
    return -1000

def rampage(user,target):
    victim = target.get_activemon()
    damage_dealing_move(user,target,False,"dragon",38,"rampage")
    if victim.is_fainted():
        victim.log(user.get_activemon().get_name()+" is tired out from its rampage!")
        user.get_activemon().status.add("recharging")
        def recharge(self,nextturn):
            user.awaitingmove = False
            nextturn.append(lambda: self.status.remove("recharging"))

        user.get_activemon().turnendcallbacks.append(recharge)


moves = {
        "facepunch": construct_damaging_move(False,"fighting",25,"facepunch"),
        "falcon punch": construct_damaging_move(False,"fire",20,"falcon punch"),
        "boulder toss": construct_damaging_move(False,"rock",22,"boulder toss"),
        "forbidden shadow assault": construct_damaging_move(False,"dark",20,"forbidden shadow assault"),
        "pilebunker": Move(pilebunker,prioritycallback=pilebunker_PCB),
        "dragon fang": construct_damaging_move(False,"dragon",23,"dragon fang"),
        "rampage": Move(rampage),
        "fire breath": construct_damaging_move(True,"fire",24,"fire breath"),
        "skydive": construct_damaging_move(False,"flying",20,"skydive"),
        }

