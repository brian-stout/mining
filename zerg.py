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
        # TODO:  Solve the coupling
        self.daddyOverlord = overlord
        self.location = Coordinates(0, 0)
        self.home = Coordinates(0, 0)
        self.returnMode = False

    def move_north(self, context):
            if context.north in '*#Z':
                return 'NORTH'
            else:
                return 'NORTH'

    def move_south(self, context):
            if context.south in '*#Z':
                return 'SOUTH'
            else:
                return 'SOUTH'

    def move_east(self, context):
            if context.east in '*#Z':
                return 'EAST'
            else:
                return 'EAST'

    def move_west(self, context):
            if context.west in '*#Z':
                return 'WEST'
            else:
                return 'WEST'

    def maintain_position(self):
            return 'CENTER'

    def leave_deployment_zone(self, context):
        if context.north in ' ':
            return self.move_north(context)
        elif context.south in ' ':
            return self.move_south(context)
        elif context.east in ' ':
            return self.move_east(context)
        elif context.west in ' ':
            return self.move_west(context)
        else:
            return False

    def move_to_home(self, context):
        
        if context.north == '_':
            self.location.y = self.home.y - 1
            return self.move_north(context)
        elif context.south ==  '_':
            self.location.y = self.home.y + 1
            return self.move_south(context)
        elif context.east == '_':
            self.location.x = self.home.x - 1
            return self.move_east(context)
        elif context.west == '_':
            self.location.x = self.home.x + 1
            return self.move_west(context)

        if self.location.x > self.home.x and context.west in ' _~*':
            return self.move_west(context)
        elif self.location.x < self.home.x and context.east in ' _~*':
            return self.move_east(context)
        elif self.location.y > self.home.y and context.south in ' _~*':
            return self.move_south(context)
        elif self.location.y < self.home.y and context.north in ' _~*':
            return self.move_north(context)
        else:
            return self.maintain_position()

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
            return self.move_north(context)
        elif instruction == 'SOUTH':
            return self.move_south(context)
        elif instruction == 'EAST':
            return self.move_east(context)
        elif instruction == 'WEST':
            return self.move_west(context)
        else:
            return self.maintain_position()

    def random_direction(self, context): 
        new = randint(0, 3)
        if new == 0 and context.north in ' ':
            return self.move_north(context)
        elif new == 1 and context.south in ' ':
            return self.move_south(context)
        elif new == 2 and context.east in ' ':
            return self.move_east(context)
        elif new == 3 and context.west in ' ':
            return self.move_west(context)
        else:
            return self.maintain_position() 

    def move(self, context):
        self.location.x = context.x
        self.location.y = context.y

        if self.returnMode == True:
            direction = self.move_to_home(context)
            if direction == 'CENTER':
                #Calls to Overlord to let it know, it's at deployment area
                self.daddyOverlord.return_zerg(self)
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

        for _ in range(6):
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
            return 'DEPLOY {} {}'.format((zerg), mapId)

        else:
            if self.returningDrones == True:
                return 'RETURN {}'.format(choice(list(self.zerg.keys())))
            else:
                return 'DEPLOY {} {}'.format(choice(list(self.zerg.keys())),
                    choice(list(self.maps.keys())))

        


