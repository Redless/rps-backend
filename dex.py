species = {
        "Crockodyle":{"atk":100,"dfn":100,"spd":100,"spa":100,"spe":100,"types":["fire"]},
        "Puncher":{"atk":150,"dfn":120,"spd":80,"spa":60,"spe":85,"types":["fighting"]},
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
    target.took_direct_damage()
    target.take_damage(damage)
    return damage

class Move:

    def __init__(self, usemove, prioritycallback = None):
        self.usemove = usemove
        self.prioritycallback = prioritycallback

    def __call__(self,user,target):
        self.usemove(user,target)

    def adjust_priority(self):
        if self.prioritycallback:
            return self.prioritycallback()
        return 0

def construct_damaging_move(isSpecial,movetype,BP,name):
    return Move(lambda x, y: damage_dealing_move(x,y,isSpecial,movetype,BP,name))

def pilebunker(user,target):
    if user.get_activemon().took_attack_this_turn():
        user.room.log(user.get_activemon().get_name()+" flinched!")
    else:
        damage_dealing_move(user,target,False,"fighting",40,"pilebunker")

moves = {
        "facepunch": construct_damaging_move(False,"fighting",25,"facepunch"),
        "falcon punch": construct_damaging_move(False,"fire",20,"falcon punch"),
        "boulder toss": construct_damaging_move(False,"rock",22,"boulder toss"),
        "forbidden shadow assault": construct_damaging_move(False,"dark",20,"forbidden shadow assault"),
        "pilebunker": Move(pilebunker,prioritycallback=lambda: -1000),
        }

