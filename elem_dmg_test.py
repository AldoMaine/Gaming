# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 08:12:30 2022

@author: aldon
"""
import random
import matplotlib.pyplot as plt



class Proc():
    """Models elemental damage from a sucessful hit over time"""
    
    def __init__(self, damage, duration):
        self.damage = damage  # damage per tick
        self.timer = duration  # ticks
    
    def step(self):
        self.timer -= 1  # reduce remaining time by one tick
        if self.timer < 0:
            self.damage = 0


def elem_dmg(fr, dpel, firing_time, rs, edps, echa, esec, acc, dfactors,
             ncycles=1000):
    """
    Compute elemental damage per firing cycle (fire time + reload).
    For each pellet that hits, there is echa chance of doing esec
    of elemental damage. Each elemental success triggers a "proc" 
    that last esec. 

    Parameters
    ----------
    fr : float
        Fire rate, shots per second
    dpel : int
        pellets per shot
    firing_time : float
        portion of cycle spent shooting (sec).
    rs : float
        reload speed sec.
    edps : float
        elemental damage rate: damage/sec.
    echa : float
        chance of initiating elemental damage per pellet.
    esec : float
        duration of elemental effect. may be extended by subsequent shots.
    acc : float
        Accuracy, percent
    dfactors : list
        Damage factor for Flesh, Shielded and Armored targets
    ncycles : int
        number of fire + reload cycles to simulate for averaging purposes. 

    Returns
    -------
    enet : float
        Average elemental damage in a firing cycle.

    """
    tick = 1/3  # seconds
    pellets_tick = fr * dpel * tick * acc/100  # pellets per tick
    firing_ticks = round(firing_time / tick)
    firing = [1]*firing_ticks + [0]*round(rs/tick)
    firing = firing * ncycles
    
    data = []

    edpm = []  # elemental dmage per mag to flesh, shield and armor
    for dfac in dfactors:
        enet = 0     
        procs = []  # Proc list
        for i in range(len(firing)):
            if firing[i]:
                prob = 1 - (1-echa/100)**pellets_tick
                if random.random() < prob:
                    procs.append(Proc(edps * dfac * tick, esec / tick))
    
            dmg = 0        
            for p in procs:
                dmg += p.damage
                p.step()
                if p.damage == 0:
                    procs.remove(p)
                
            enet += dmg
            data.append(dmg)
            
        edpm.append(enet / ncycles)
    
    return edpm, data, firing


def kinetic_dmg(dmg, dpel, mag, bpsh, acc, dfactors):
    """
    Compute kinetic damage per firing cycle.

    Parameters
    ----------
    dmg : float
        Damage per pellet.
    dpel : int
        Pellets per shot.
    mag : int
        Magazine size.  Number of bullets per clip.
    bpsh : int
        Bullets per shot.
    acc : float
        Accuracy.
    dfactors : list
        Damage factor for Flesh, Shielded and Armored targets

    Returns
    -------
    float : Net kinetic damage per firing cycle.

    """
    shots_mag = mag / bpsh
    
    ans = [fac * dmg * dpel * shots_mag * acc / 100 for fac in dfactors]

    return ans


# Test case data
# Tactical something
dmg = 761
dpel = 1  # pellets per shot
acc = 93.0
fr = 6.9  # shots/sec
rs = 1.5
mag = 21  # magazine size
# Elem type Corrosive
edps = 245.1
echa = 14.4
esec = 8
dfactors = [.9, .75, 1.5] # corrosion damage to flesh, shields and armor

bpsh = 2  # bullets per shot
ncycles = 1000



firing_time =  mag / (fr * bpsh)  

netedmg, data, firing = elem_dmg(fr, dpel, firing_time, rs, edps, echa, esec,
                                 acc, dfactors, ncycles)

netkdmg = kinetic_dmg(dmg, dpel, mag, bpsh, acc, [1,1,.8])

print("Avg Dmg per cycle: {:.1f} kinetic, {:.1f} elemental".format(
    sum(netkdmg)/3, sum(netedmg)/3))
print("Cycle time {:.2f} sec.".format(firing_time + rs))
print("Net DPS: {:.1f}".format((sum(netedmg)/3 + sum(netkdmg)/3)/ (firing_time + rs)))  # Avg Damage per second

if ncycles < 21:
    plt.bar(range(len(data)), data)
    plt.bar(range(len(data)), [f*50 for f in firing])
       
      
 