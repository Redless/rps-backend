species = {
        "Crockodyle":{"atk":100,"dfn":100,"spd":100,"spa":100,"spe":100,"types":["fire"]},
        "Puncher":{"atk":140,"dfn":100,"spd":60,"spa":40,"spe":60,"types":["fighting"]},
}

typekey = {"normal":0,"fighting":1,"flying":2,"rock":3,"steel":4,"dragon":5,"fire":6,"water":7,"grass":8,"psychic":9,"ghost":10,"dark":11}
typematchup = [[ 1, 1, 1,.5,.5, 1, 1, 1, 1, 1, 0, 1], #offensive type THEN defensive type order..
               [ 2, 1,.5, 2, 2, 1, 1, 1, 1,.5, 0, 2],
               [ 1, 2, 1,.5,.5, 1, 1, 1, 2, 1, 1, 1],
               [ 1,.5, 2, 1,.5, 1, 2, 1, 1, 1, 1, 1],
               [ 1, 1, 1, 2,.5, 1,.5,.5, 1, 1, 1, 1],
               [ 1, 1, 1, 1,.5, 2, 1, 1, 1, 1, 1, 1],
               [ 1, 1, 1,.5, 2,.5,.5,.5, 2, 1, 1, 1],
               [ 1, 1, 1, 2, 1,.5, 2,.5,.5, 1, 1, 1],
               [ 1, 1,.5, 2,.5,.5,.5, 2,.5, 1, 1, 1],
               [ 1, 2, 1, 1,.5, 1, 1, 1, 1,.5, 1, 0],
               [ 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2,.5],
               [ 1,.5, 1, 1, 1, 1, 1, 1, 1, 2, 2,.5]]

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
    target.take_damage(damage)
    return damage

moves = {
        "facepunch": lambda x, y: damage_dealing_move(x,y,False,"fighting",25,"facepunch"),
        "surf": lambda x, y: damage_dealing_move(x,y,True,"water",20,"surf"),
        "rockfall": lambda x, y: damage_dealing_move(x,y,False,"rock",18,"rockfall"),
        }

