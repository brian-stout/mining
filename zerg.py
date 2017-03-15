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
        self.daddyOverlord = overlord
        self.location = Coordinates(0, 0)
        self.returnMode = False

    def move_north(self):
            self.location.y += 1
            return 'NORTH'

    def move_south(self):
            self.location.y -= 1
            return 'SOUTH'

    def move_east(self):
            self.location.x += 1
            return 'EAST'

    def move_west(self):
            self.location.x -= 1
            return 'WEST'

    def maintain_position(self):
            return 'CENTER'

    def move_to_home(self):
        if self.location.x > 0:
            return self.move_south()
        elif self.location.x < 0:
            return self.move_north()
        elif self.location.y > 0:
            return self.move_west()
        elif self.location.y < 0:
            return self.move_east()
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
            return self.move_north()
        elif instruction == 'SOUTH':
            return self.move_south()
        elif instruction == 'EAST':
            return self.move_east()
        elif instruction == 'WEST':
            return self.move_west()
        else:
            return self.maintain_position()

    def random_direction(self, context): 
        new = randint(0, 3)
        if new == 0 and context.north in ' ':
            return self.move_north()
        elif new == 1 and context.south in ' ':
            return self.move_south()
        elif new == 2 and context.east in ' ':
            return self.move_east()
        elif new == 3 and context.west in ' ':
            return self.move_west()
        else:
            return self.maintain_position() 

    def move(self, context):
        if self.returnMode == True:
            direction = self.move_to_home()
            if direction:
                return direction

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
        self.ticksLeft = ticks
        self.origin = Coordinates(0,0)
        self.returningDrones = False

        for _ in range(6):
            z = Drone(self)
            self.zerg[id(z)] = z

    # Function used to determined the mininum number of changes required to
    #   go from one coordinate to another
    def determine_distance(self, pair1, pair2):
        return abs(pair1.x - pair2.x) + abs(pair1.y - pair2.y)

    def add_map(self, map_id, summary):
        self.maps[map_id] = summary

    def action(self):
        """for zerg in self.zerg.values():
            distance = self.determine_distance(self.origin, zerg.location)
            if distance < (self.ticksLeft + 2):
                self.returningDrones = True
                zerg.returnMode = True"""

        for key in self.zerg:
            return 'DEPLOY {} {}'.format((key), choice(list(self.maps.keys())))

        act = randint(0, 3)
        if act == 0:
            return 'RETURN {}'.format(choice(list(self.zerg.keys())))


