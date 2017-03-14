#!/usr/local/bin/python

from map import Map
import zerg

TICKS = 100

c = zerg.Overlord()

#for n in range(3):
    #m = Map(20, 10)
    #maps[id(m)] = m

maps = { n: Map(10, 5) for n in range(3) }
for n in maps:
    c.add_map(n, maps[n].summary())

zerg_locations = { n: None for n in c.zerg }
print(zerg_locations)

mined = 0

for _ in range(TICKS):
    act = c.action()
    print(act)
    if act.startswith('DEPLOY'):
        _, z_id, map_id = act.split()
        z_id = int(z_id)
        map_id = int(map_id)
            
        if zerg_locations[z_id] is None:
            if maps[map_id].add_zerg(c.zerg[z_id]):
                zerg_locations[z_id] = map_id

    elif act.startswith('RETURN'):
        _, z_id = act.split()
        z_id = int(z_id)

        if zerg_locations[z_id] is not None:
            v = maps[map_id].remove_zerg(z_id)
            if v is not None:
                zerg_locations[z_id] = None
                mined += v

    else:
        pass

    for n in maps:
        maps[n].tick()
        print(maps[n])

print(mined)
