species = {
        "Puncher":{"atk":150,"dfn":120,"spd":80,"spa":60,"spe":85,"types":["fighting"]},
        "Aggrobull":{"atk":150,"dfn":100,"spd":100,"spa":105,"spe":140,"types":["dragon"]},
        "Serpyre":{"atk":130,"dfn":80,"spa":130,"spd":80,"spe":120,"types":["fire"]},
        "Wavoracle":{"atk":70,"dfn":120,"spa":110,"spd":130,"spe":90,"types":["water"]},
        "Falcoren":{"atk":135,"dfn":100,"spa":70,"spd":70,"spe":145,"types":["flying"]},
        "Hysteridoll":{"atk":100,"dfn":100,"spa":110,"spd":135,"spe":70,"types":["psychic"]},
        "Noklu":{"atk":120,"dfn":110,"spa":90,"spd":120,"spe":100,"types":["dark"]},
        "Paleosaurus":{"atk":110,"dfn":150,"spa":30,"spd":120,"spe":45,"types":["rock"]},
        "LZC-3000":{"atk":80,"dfn":130,"spa":110,"spd":110,"spe":60,"types":["steel"]},
        "Poltervice":{"atk":60,"dfn":80,"spa":125,"spd":135,"spe":110,"types":["ghost"]},
        "Heartbreaker":{"atk":130,"dfn":100,"spa":70,"spd":100,"spe":135,"types":["normal"]},
        "Moldleaf":{"atk":80,"dfn":150,"spa":110,"spd":120,"spe":55,"types":["grass"]},
}

typekey = {"normal":0,"fighting":1,"flying":2,"rock":3,"steel":4,"dragon":5,"fire":6,"water":7,"grass":8,"psychic":9,"ghost":10,"dark":11}
typematchup = [[ 1, 1, 1,.5,.5, 1, 1, 1, 1, 1, 0, 1], #normal #offensive type THEN defensive type order..
               [ 2, 1,.5, 2, 2, 1, 1, 1, 1,.5, 0, 2], #fighting
               [ 1, 2, 1,.5,.5, 1, 1, 1, 2, 1, 1, 1], #flying
               [ 1,.5, 2, 1,.5, 1, 2, 1, 1, 1, 1, 1], #rock
               [ 1, 1, 1, 2,.5, 1,.5,.5, 1, 1, 1, 1], #steel
               [ 1, 1, 1, 1,.5, 2, 1, 1, 1, 1, 1, 1], #dragon
               [ 1, 1, 1,.5, 2,.5,.5,.5, 2, 1, 1, 1], #fire
               [ 1, 1, 1, 2, 1,.5, 2,.5,.5, 1, 1, 1], #water
               [ 1, 1, 1, 2,.5,.5,.5, 2,.5, 1, 1, 1], #grass
               [ 1, 2, 1, 1,.5, 2, 1, 2, 1,.5, 1, 0], #psychic
               [ 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2,.5], #ghost
               [ 1,.5, 1, 1, 1, 1, 1, 1, 1, 2, 2,.5]] #dark

def damage_dealing_move(user,target,isSpecial,movetype,movepower,movename):
    user = user.get_activemon()
    target = target.get_activemon()
    user.side.room.log(user.get_name()+" used "+movename+"!")
    if not target:
        user.log("But there was no target...")
        return 0
    dmgmod = user.damage_calc_inflict()
    dmgmod *= target.damage_calc_receive()
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
        damage = max(int(user.get_spa()*movepower*typeAdv/target.get_spd()),1)
    else:
        damage = max(int(user.get_atk()*movepower*typeAdv/target.get_dfn()),1)
    user.side.room.log(target.get_name()+" took "+str(damage)+" percent!")
    target.take_damage(damage)
    target.took_direct_damage(damage)
    return damage
    #when you update this, also update tsunami warning below (I'm sorry)

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

    def movevalidcallback(self,isMove,choice):
        return True

    def get_str(self):
        return self.name

    def turnendcallback(self):
        pass

    def preturnendcallback(self):
        pass

    def remove(self):
        self.mon.remove_status(self)

    def tookdirectdamagecallback(self):
        pass

    def knockedoutcallback(self):
        self.remove()

    def abouttousemovecallback(self):
        return False # if it returns true, prevents them from using a move

    def prioritycallback(self):
        return 0 #add speed to user

    def switchedoutcallback(self):
        self.remove()

    def damagecalccallbackattacker(self):
        return 1

    def damagecalccallbackdefender(self):
        return 1

    def get_visible(self):
        return True

class FieldEffect:

    def __init__(self,side,name):
        self.side = side
        self.name = name

    def movevalidcallback(self,isMove,choice):
        return True

    def get_str(self):
        return self.name

    def remove(self):
        self.side.remove_effect(self)

    def turnendcallback(self):
        pass

    def preturnendcallback(self):
        pass

    def get_visible(self):
        return True

    def switchedincallback(self):
        pass

    def switchedoutcallback(self):
        pass

    def hazardclearcallback(self):
        pass

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
    user.switched_out()
    if user.get_activemon():
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

def tsunamiwarning(user,target):
    user.log(user.get_activemon().get_name()+" used tsunami warning!")
    user = user.get_activemon()
    dmgmod = user.damage_calc_inflict()
    if "water" in user.types:
        STAB = 1.5
    else:
        STAB = 1
    spa = user.get_spa()
    def tsunami(target):
        target.log("The tsunami hit "+target.get_name()+"!")
        dmgmod2 = target.damage_calc_receive()
        typeAdv = 1
        for x in target.types:
            typeAdv *= typematchup[typekey["water"]][typekey[x]]
        if typeAdv == 0:
            user.side.room.log("It had no effect!")
            return 0
        if typeAdv < 1:
            user.side.room.log("It's not very effective...")
        if typeAdv > 1:
            user.side.room.log("It's super effective!")
        damage = max(int(spa*35*STAB*dmgmod*dmgmod2*typeAdv/target.get_spd()),1)
        target.log(target.get_name()+" took "+str(damage)+" percent!")
        target.take_damage(damage)
    class TsunamiEffect(FieldEffect):
        def __init__(self,side):
            FieldEffect.__init__(self,side,"crashing waves")
            self.turns = 2
        def preturnendcallback(self):
            if self.turns == 2:
                self.side.log("You can hear the distant sound of waves.")
                self.turns = 1
            elif self.turns == 1:
                self.side.log("The sound of waves is getting louder!")
                self.name = "nearby waves"
                self.turns = 0
            else:
                self.remove()
                self.side.log("The tsunami crashes down!")
                targ = target.get_activemon()
                if targ:
                    tsunami(targ)
    for effect in user.side.fieldeffects:
        if (effect.get_str() == "nearby waves") or (effect.get_str() == "crashing waves"):
            user.log("A tsunami was already warned of!")
            return
    user.side.add_effect(TsunamiEffect(user.side))

def recklessdescent(user,target):
    dmg = damage_dealing_move(user,target,False,"flying",35,"reckless descent")
    if dmg:
        recoil = max(dmg//3,1)
        user.log(user.get_activemon().get_name()+" took "+str(recoil)+" percent recoil!")
        user.get_activemon().take_damage(recoil)

def brainwash(user,target):
    user.log(user.get_activemon().get_name()+" used brainwash!")
    target = target.get_activemon()
    if not target:
        return
    user.log(target.get_name()+" was brainwashed!")
    class BrainwashStatus(Status):
        def __init__(self,mon):
            Status.__init__(self,mon,"brainwashed")
            self.oldtypes = mon.types
            mon.types = ["psychic"]
        def remove(self):
            Status.remove(self)
            self.mon.types = self.oldtypes
    target.add_status(BrainwashStatus(target))

def resonate(user,target):
    if "psychic" in target.get_activemon().types:
        damage_dealing_move(user,target,True,"psychic",72,"resonate")
    else:
        damage_dealing_move(user,target,True,"psychic",18,"resonate")

def rivalry(user,target):
    user.log(user.get_activemon().get_name()+" used rivalry!")
    for status in user.get_activemon().status:
        if status.get_str() == "rival":
            return
    if target.get_activemon():
        user.log(user.get_activemon().get_name()+" and "+target.get_activemon().get_name()+" became rivals!")
    else:
        return
    class RivalryStatus(Status):
        def __init__(self,mon1,mon2):
            self.name = "rival"
            self.mon1 = mon1
            self.mon2 = mon2
        def remove(self):
            self.mon1.remove_status(self)
            self.mon2.remove_status(self)
        def damagecalccallbackdefender(self):
            return 1.2
    rivalrystatus = RivalryStatus(user.get_activemon(),target.get_activemon())
    user.get_activemon().add_status(rivalrystatus)
    target.get_activemon().add_status(rivalrystatus)
    
def disastervision(user,target):
    user.log(user.get_activemon().get_name()+" used visions of disaster!")
    mon = user.get_activemon()
    mon.spdboosts += 1
    mon.dfnboosts += 1
    mon.speboosts -= 2
    user.log(user.get_activemon().get_name()+"'s defense rose!")
    user.log(user.get_activemon().get_name()+"'s special defense rose!")
    user.log(user.get_activemon().get_name()+"'s speed harshly fell!")

def deathdance(user,target):
    user.log(user.get_activemon().get_name()+" used death dance!")
    class PerishStatus(Status):
        def __init__(self,mon):
            Status.__init__(self,mon,"perish count: ")
            self.count = 4
        def get_str(self):
            return self.name+str(self.count)
        def turnendcallback(self):
            self.count -= 1
            self.mon.log(self.mon.get_name()+"'s perish count fell to "+str(self.count)+"!")
            if self.count == 0:
                self.mon.take_damage(100)
    alreadyPerishing = False
    for status in user.get_activemon().status:
        if "perish count: " in status.get_str():
            alreadyPerishing = True
    if not alreadyPerishing:
        user.get_activemon().add_status(PerishStatus(user.get_activemon()))
    if target.get_activemon():
        alreadyPerishing = False
        for status in target.get_activemon().status:
            if "perish count: " in status.get_str():
                alreadyPerishing = True
        if not alreadyPerishing:
            target.get_activemon().add_status(PerishStatus(target.get_activemon()))

def lockdown(user,target):
    user.log(user.get_activemon().get_name()+" used lockdown!")
    for effect in user.fieldeffects:
        if effect.get_str() == "lockdown":
            user.log("Lockdown is already in effect!")
            return
    class LockdownEffect(FieldEffect):
        def __init__(self,side):
            FieldEffect.__init__(self,side,"lockdown")
            self.turnused = False
        def turnendcallback(self):
            if self.turnused:
                self.remove()
            self.turnused = True
        def movevalidcallback(self,isMove,choice):
            return isMove
    user.add_effect(LockdownEffect(user))
    target.add_effect(LockdownEffect(target))

def ambush(user,target):
    for effect in target.fieldeffects:
        if effect.get_str() == "ambush prepped":
            if effect.sprung:
                damage_dealing_move(user,target,False,"dark",45,"ambush")
            else:
                damage_dealing_move(user,target,False,"dark",15,"ambush")
            return
                
    print("something went wrong with ambush")
def ambush_PCB(user):
    class AmbushprepEffect(FieldEffect):
        def __init__(self,side):
            FieldEffect.__init__(self,side,"ambush prepped")
            self.sprung = False
        def turnendcallback(self):
            self.remove()
        def switchedoutcallback(self):
            self.sprung = True
        def get_visible(self):
            return False
    user.otherside.add_effect(AmbushprepEffect(user.otherside))
    return 0

def lastword(user,target,onSwitch=False):
    for effect in target.fieldeffects:
        if effect.get_str() == "pursuit prepped":
            if effect.pursued:
                return
            effect.pursued = True
            damage_dealing_move(user,target,False,"dark",20 if onSwitch else 10,"last word")
            return
    print("something went wrong with lastword")

def lastword_PCB(user):
    class PursuedEffect(FieldEffect):
        def __init__(self,side):
            FieldEffect.__init__(self,side,"pursuit prepped")
            self.pursued = False
        def turnendcallback(self):
            self.remove()
        def get_visible(self):
            return False
        def switchedoutcallback(self):
            lastword(user,user.otherside,onSwitch=True)
    user.otherside.add_effect(PursuedEffect(user.otherside))
    return 0

def rocksplosion(user,target):
    dmg = damage_dealing_move(user,target,False,"rock",60,"rocksplosion")
    user.log(user.get_activemon().get_name()+" exploded!")
    user.get_activemon().take_damage(100)

def bonecrushtackle(user,target):
    dmg = damage_dealing_move(user,target,False,"rock",10,"bonecrush tackle")
    if dmg:
        class BonecrushedStatus(Status):
            def __init__(self,mon):
                Status.__init__(self,mon,"bonecrushed")
                self.turnused = False
            def turnendcallback(self):
                if self.turnused:
                    self.remove()
                self.turnused = True
            def prioritycallback(self):
                return -1000
        mon = target.get_activemon()
        if mon:
            mon.add_status(BonecrushedStatus(mon))

def boneshardscatter(user,target):
    user.log(user.get_activemon().get_name()+" used boneshard scatter!")
    for effect in target.fieldeffects:
        if effect.get_str() == "boneshards":
            return
    class BoneshardEffect(FieldEffect):
        def switchedincallback(self):
            mon = self.side.get_activemon()
            typeAdv = 12
            for x in mon.types:
                typeAdv *= typematchup[typekey["rock"]][typekey[x]]
            mon.log("Pointed stones dug into "+mon.get_name())
            mon.take_damage(typeAdv)
        def hazardclearcallback(self):
            self.remove()
    target.add_effect(BoneshardEffect(target,"boneshards"))

def selfdestruct(user,target):
    dmg = damage_dealing_move(user,target,False,"normal",60,"selfdestruct")
    user.log(user.get_activemon().get_name()+" exploded!")
    user.get_activemon().take_damage(100)

def draconicbombardment(user,target):
    dmg = damage_dealing_move(user,target,True,"dragon",34,"draconic bombardment")
    if dmg:
        user.log(user.get_activemon().get_name()+"'s special attack harshly fell!")
        user.get_activemon().spaboosts -= 2

def amplification(user,target):
    user.log(user.get_activemon().get_name()+" used amplification!")
    user.log(user.get_activemon().get_name()+"'s special attack sharply rose!")
    user.get_activemon().spaboosts += 2

def secureperimeter(user,target):
    dmg = damage_dealing_move(user,target,False,"normal",5,"secure perimeter")
    if dmg:
        user.log(user.get_activemon().get_name()+" secured the perimeter!")
        for callback in [i for i in user.fieldeffects]:
            callback.hazardclearcallback()

def rebound(user,target):
    dmg = damage_dealing_move(user,target,False,"normal",16,"rebound")
    if dmg:
        user.log(user.get_activemon().get_name()+" bounced away!")
        if user.get_num_living() == 1:
            user.log("BUT THERE'S NOWHERE LEFT TO RUN")
            return
        user.switched_out()
        if user.get_activemon():
            user.activemon = None
            user.panicking = True
            user.await_move()

def powerrite(user,target):
    user.log(user.get_activemon().get_name()+" used rite of power!")
    user.log(user.get_activemon().get_name()+"'s special attack sharply rose!")
    user.log(user.get_activemon().get_name()+"'s speed sharply rose!")
    user.log(user.get_activemon().get_name()+" cut its HP!")
    user.get_activemon().spaboosts += 2
    user.get_activemon().speboosts += 2
    user.get_activemon().take_damage(40)

def entwinefate(user,target):
    user.log(user.get_activemon().get_name()+" used entwine fate!")
    class FateStatus(Status):
        def __init__(self,mon):
            Status.__init__(self,mon,"entwined fate")
            self.used = False
        def tookdirectdamagecallback(self):
            if self.used:
                return
            if not self.mon.is_fainted():
                deadnow = self.mon.side.otherside.get_activemon()
                if deadnow:
                    self.mon.log("It seems their fates were joined...")
                    deadnow.take_damage(100)
        def turnendcallback(self):
            if self.used:
                self.remove()
            self.name = "frayed fate"
            self.used = True
        def knockedoutcallback(self):
            pass
    for status in user.get_activemon().status:
        if status.get_str() == "frayed fate":
            return
    user.get_activemon().add_status(FateStatus(user.get_activemon()))

def gigadrain(user,target):
    dmg = damage_dealing_move(user,target,True,"grass",20,"giga drain")
    if dmg:
        user.log(user.get_activemon().get_name()+" restored its health!")
        user.get_activemon().health = min(100,user.get_activemon().health + max(1,int(dmg/3)))

def roots(user,target):
    user.log(user.get_activemon().get_name()+" used entangling roots!")
    class RootStatus(Status):
        def __init__(self,mon):
            Status.__init__(self,mon,"entangling roots")
            self.turnsused = 0
        def movevalidcallback(self,isMove,choice):
            return isMove
        def turnendcallback(self):
            self.turnsused += 1
            if self.turnsused == 2:
                self.name = "loose roots"
            if self.turnsused == 3:
                self.remove()
    target.get_activemon().add_status(RootStatus(target.get_activemon()))

def leechseed(user,target):
    user.log(user.get_activemon().get_name()+" used leech seed!")
    if not target.get_activemon():
        return
    for status in target.get_activemon().status:
        if status.name == "leech seed":
            return
    class SeedStatus(Status):
        def preturnendcallback(self):
            target = self.mon.side.otherside.get_activemon()
            if self.mon and target:
                target.log(target.get_name()+" was drained by leech seed!")
                dmg = min(10,target.health)
                target.take_damage(dmg)
                self.mon.health = min(100,self.mon.health + max(1,dmg))
    target.get_activemon().add_status(SeedStatus(target.get_activemon(),"leech seed"))

def spore(user,target):
    user.log(user.get_activemon().get_name()+" used spore!")
    if not target.get_activemon():
        return
    for effect in target.fieldeffects:
        if " is asleep" in effect.get_str():
            return
    class SleepStatus(Status):
        def __init__(self,mon):
            Status.__init__(self,mon,"asleep")
            self.turnsasleep = 0
        def switchedoutcallback(self):
            pass
        def abouttousemovecallback(self):
            if not self.mon.side.action[0]:
                return
            self.turnsasleep += 1
            if self.turnsasleep == 3:
                self.remove()
                self.mon.log(self.mon.get_name()+" woke up!")
                for effect in self.mon.side.fieldeffects:
                    if " is asleep" in effect.get_str():
                        effect.remove()
                        return False
                self.mon.log("something went wrong")
            self.mon.log(self.mon.get_name()+" is fast asleep!")
            return True
    target.get_activemon().add_status(SleepStatus(target.get_activemon()))
    target.add_effect(FieldEffect(target,target.get_activemon().get_name()+" is asleep"))


moves = {
        "facepunch": construct_damaging_move(False,"fighting",25,"facepunch"),
        "falcon punch": construct_damaging_move(False,"fire",20,"falcon punch"),
        "boulder toss": construct_damaging_move(False,"rock",22,"boulder toss"),
        "shadow strike": construct_damaging_move(False,"dark",20,"shadow strike"),
        "waterfall": construct_damaging_move(False,"water",22,"waterfall"),
        "phantom slice": construct_damaging_move(False,"ghost",20,"phantom slice"),
        "vine whip": construct_damaging_move(False,"grass",20,"vine whip"),
        "rebound": Move(rebound,"normal"),
        "telekinesis": construct_damaging_move(False,"psychic",20,"telekinesis"),
        "pilebunker": Move(pilebunker,"fighting",prioritycallback=pilebunker_PCB),
        "dragon fang": construct_damaging_move(False,"dragon",23,"dragon fang"),
        "rampage": Move(rampage,"dragon"),
        "fire breath": construct_damaging_move(True,"fire",24,"fire breath"),
        "skydive": construct_damaging_move(False,"flying",20,"skydive"),
        "smoldering jaws": construct_damaging_move(False,"fire",24,"smoldering jaws"),
        "retreat": Move(retreat,"normal"),
        "pilot light": Move(pilotlight,"fire"),
        "tsunami warning": Move(tsunamiwarning,"water"),
        "wave call": construct_damaging_move(True,"water",20,"wave call"),
        "mind break": construct_damaging_move(True,"psychic",22,"mind break"),
        "reckless descent": Move(recklessdescent,"flying"),
        "rivalry": Move(rivalry,"dark"),
        "brainwash": Move(brainwash,"psychic"),
        "resonate": Move(resonate,"psychic"),
        "visions of disaster": Move(disastervision,"psychic"),
        "death dance": Move(deathdance,"dark"),
        "ambush": Move(ambush,"dark",prioritycallback=ambush_PCB),
        "lockdown": Move(lockdown,"dark"),
        "last word": Move(lastword,"dark",prioritycallback=lastword_PCB),
        "rocksplosion": Move(rocksplosion,"rock"),
        "boneshard scatter": Move(boneshardscatter,"rock"),
        "bonecrush tackle": Move(bonecrushtackle,"rock"),
        "metal ion laser": construct_damaging_move(True,"steel",23,"metal ion laser"),
        "draconic bombardment": Move(draconicbombardment,"dragon"),
        "amplification": Move(amplification,"steel"),
        "secure perimeter": Move(secureperimeter,"normal"),
        "selfdestruct": Move(selfdestruct,"normal"),
        "rite of power": Move(powerrite,"ghost"),
        "entwine fate": Move(entwinefate,"ghost"),
        "hex": construct_damaging_move(True,"ghost",22,"hex"),
        "giga drain": Move(gigadrain,"grass"),
        "entangling roots": Move(roots,"grass"),
        "leech seed": Move(leechseed,"grass"),
        "spore": Move(spore,"grass"),
        }
