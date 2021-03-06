#!/usr/local/bin/python

from map import Map
import zerg
import os
from time import sleep
import astar
import graph

TICKS = 1000

c = zerg.Overlord(TICKS)

maps = { n: Map(40, 20) for n in range(3) }
for n in maps:
    c.add_map(n, maps[n].summary())

zerg_locations = { n: None for n in c.zerg }
zerg_health = { n: 40 for n in c.zerg }
print(zerg_locations)

mined = 0

for _ in range(TICKS):
    if mined >= 135:
        break
    act = c.action()
    print(act)
    if act.startswith('DEPLOY'):
        _, z_id, map_id = act.split()
        z_id = int(z_id)
        map_id = int(map_id)

        if zerg_locations[z_id] is None:
            if maps[map_id].add_zerg(c.zerg[z_id], zerg_health[z_id]):
                zerg_locations[z_id] = map_id

    elif act.startswith('RETURN'):
        _, z_id = act.split()
        z_id = int(z_id)

        if zerg_locations[z_id] is not None:
            map_id = zerg_locations[z_id]
            extracted, hp = maps[map_id].remove_zerg(z_id)
            if extracted is not None:
                zerg_locations[z_id] = None
                zerg_health[z_id] = hp
                mined += extracted

    else:
        pass

    #Haubrich's auto player implementation
    #os.system("clear") 
    os.system("clear")
    for n in maps:
        maps[n].tick()
        graph = c.get_graph(n)
        if graph:
            print()
            #print(graph)
            print(graph.mineralsMined)
            print(graph.complete)
        print(maps[n], end='\n')
    print(c.ticksLeft)
    sleep(0.05)


print(mined)
