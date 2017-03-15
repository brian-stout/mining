#!/usr/local/bin/python

from random import randint, choice

class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Drone:
    tick = 0
    def __init__(self, overlord):
        self.instructionQueue = ['NORTH', 'NORTH', 'NORTH', 'NORTH', 'EAST', 'EAST', 'SOUTH', 'SOUTH', 'WEST', 'WEST', 'WEST', 'WEST', 'WEST']
        self.daddyOverlord = overlord
        self.location = Coordinates(0, 0)

    def move_north(self):
            self.location.y += 1
            self.update_distance()
            return 'NORTH'

    def move_south(self):
            self.location.y -= 1
            self.update_distance()
            return 'SOUTH'

    def move_east(self):
            self.location.x += 1
            self.update_distance()
            return 'EAST'

    def move_west(self):
            self.location.x -= 1
            self.update_distance()
            return 'WEST'

    def maintain_position(self):
            return 'CENTER'

    def move(self, context):
        if context.north == '*':
            return self.move_north()
        if context.south == '*':
            return self.move_south()
        elif context.east == '*':
            return self.move_east()
        elif context.west == '*':
            return self.move_west()

        if self.instructionQueue:
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

        new = randint(0, 3)
        if new == 0 and context.north in '* ':
            return 'NORTH'
        elif new == 1 and context.south in '* ':
            return 'SOUTH'
        elif new == 2 and context.east in '* ':
            return 'EAST'
        elif new == 3 and context.west in '* ':
            return 'WEST'
        else:
            return 'CENTER'



class Overlord:
    def __init__(self):
        self.maps = {}
        self.zerg = {}

        for _ in range(6):
            z = Drone(self)
            self.zerg[id(z)] = z

    def determine_distance(self, pair1, pair2):
        return abs(pair1.x - pair2.x) + abs(pair1.y - pair2.y)

    def add_map(self, map_id, summary):
        self.maps[map_id] = summary

    def action(self):
        act = randint(0, 3)
        if act == 0:
            return 'RETURN {}'.format(choice(list(self.zerg.keys())))
        else:
            return 'DEPLOY {} {}'.format(choice(list(self.zerg.keys())),
                    choice(list(self.maps.keys())))

