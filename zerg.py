#!/usr/local/bin/python

from random import randint, choice

class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Drone:
    tick = 0
    def __init__(self, overlord):
        self.instructionQueue = []
        self.mapId = 0
        self.overlord = overlord
        self.location = Coordinates(0, 0)
        self.home = Coordinates(0, 0)
        self.returnMode = False

    def leave_deployment_zone(self, context):
        if context.north in ' ':
            return 'NORTH'
        elif context.south in ' ':
            return 'SOUTH'
        elif context.east in ' ':
            return 'EAST'
        elif context.west in ' ':
            return 'WEST'
        else:
            return False

    def move_to_home(self, context):
        if self.location.x > self.home.x and context.west in ' _~*':
            return 'WEST'
        elif self.location.x < self.home.x and context.east in ' _~*':
            return 'EAST'
        elif self.location.y > self.home.y and context.south in ' _~*':
            return 'SOUTH'
        elif self.location.y < self.home.y and context.north in ' _~*':
            return 'NORTH'
        else:
            return 'CENTER'

    def focus_minerals(self, context):
        if context.north in '*':
            return 'NORTH'
        elif context.south in '*':
            return 'SOUTH'
        elif context.east in '*':
            return 'EAST'
        elif context.west in '*':
            return 'WEST'
        else:
            return False 
    
    def follow_instruction(self):
        instruction = self.instructionQueue.pop(-1)

        if instruction == 'NORTH':
            return 'NORTH'
        elif instruction == 'SOUTH':
            return 'SOUTH'
        elif instruction == 'EAST':
            return 'EAST'
        elif instruction == 'WEST':
            return 'WEST'
        else:
            return 'CENTER'


    def random_direction(self, context): 
        new = randint(0, 3)
        if new == 0 and context.north in ' ':
            return 'NORTH'
        elif new == 1 and context.south in ' ':
            return 'SOUTH'
        elif new == 2 and context.east in ' ':
            return 'EAST'
        elif new == 3 and context.west in ' ':
            return 'WEST'
        else:
            return 'CENTER'

    def update_map(self, context):
        if self.overlord.scoutedMap[self.mapId]:
            self.overlord.update_map(self.mapId, context)
        else:
            self.overlord.create_map(self.mapId, context)

    def move(self, context):
        self.location.x = context.x
        self.location.y = context.y

        if self.returnMode == True:
            direction = self.move_to_home(context)
            if direction == 'CENTER':
                #Calls to Overlord to let it know, it's at deployment area
                self.overlord.return_zerg(self)
                return direction
            elif direction:
                return direction

        elif self.home.x == 0 and self.home.y == 0:
            self.home.x = context.x
            self.home.y = context.y
            return self.leave_deployment_zone(context)

        direction = self.focus_minerals(context)
        if direction:
            return direction

        if self.instructionQueue:
            direction = self.follow_instruction()
            if direction:
                return direction

        direction = self.random_direction(context)
        if direction:
            return direction

class Overlord:
    def __init__(self, ticks):
        self.maps = {}
        self.zerg = {}
        self.zergDropList = []
        self.nextMap = 0
        self.zergReturnList = []
        self.ticksLeft = ticks
        self.origin = Coordinates(0,0)
        self.returningDrones = False

        for number in range(6):
            z = Drone(self)
            self.zerg[id(z)] = z

        for key in self.zerg:
            self.zergDropList.append(key)

    # Function used to determined the mininum number of changes required to
    #   go from one coordinate to another
    def determine_distance(self, pair1, pair2):
        return abs(pair1.x - pair2.x) + abs(pair1.y - pair2.y)

    def add_map(self, map_id, summary):
        self.maps[map_id] = summary

    def return_zerg(self, zergObject):
        zergID = id(zergObject)
        if zergID in self.zergReturnList:
            pass
        else:
            self.zergReturnList.append(zergID)


    def update_map(self, mapId, context):
        m = self.scoutedMap[mapId]
        
        if m.dataAssigned == True:
            m.update_map(context)
        else:
            print("DEBUG: ASSIGNING DATA TO " + str(mapId))
            m.data_assignment(context)   

    def action(self):
        if self.ticksLeft < 30 and self.returningDrones == False:
            self.returningDrones = True
            for zerg in self.zerg.values():
                zerg.returnMode = True

        if self.zergReturnList and self.returningDrones == True:
            zergID = self.zergReturnList.pop(0)
            return 'RETURN {}'.format(zergID)

        elif self.zergDropList:
            zerg = self.zergDropList.pop(0)
            mapId = self.nextMap
            self.nextMap += 1
            if self.nextMap > 2:
                self.nextMap = 0
            self.zerg[zerg].mapId = mapId
            return 'DEPLOY {} {}'.format((zerg), mapId)

        else:
            if self.returningDrones == True:
                return 'RETURN {}'.format(choice(list(self.zerg.keys())))
            else:
                return 'DEPLOY {} {}'.format(choice(list(self.zerg.keys())),
                    choice(list(self.maps.keys())))

        


