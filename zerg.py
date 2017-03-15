#!/usr/local/bin/python

from random import randint, choice

class Drone:
    tick = 0
    def __init__(self):
        self.instructionQueue = []

    def follow_instruction():
        instruction = instructionQueue.pop(0)
        return instruction

    def move(self, context):
        if context.north == '*':
            return 'NORTH'
        if context.south == '*':
            return 'SOUTH'
        elif context.east == '*':
            return 'EAST'
        elif context.west == '*':
            return 'WEST'

        if self.instructionQueue:
            self.follow_instruction()

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
            z = Drone()
            self.zerg[id(z)] = z

    def add_map(self, map_id, summary):
        self.maps[map_id] = summary

    def action(self):
        act = randint(0, 3)
        if act == 0:
            return 'RETURN {}'.format(choice(list(self.zerg.keys())))
        else:
            return 'DEPLOY {} {}'.format(choice(list(self.zerg.keys())),
                    choice(list(self.maps.keys())))

