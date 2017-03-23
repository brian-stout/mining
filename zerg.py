#!/usr/local/bin/python
from graph import Vertex, Graph
from astar import *
from random import randint, choice

class Drone:
#ZERG STATE
#1. Get off deployment Zone
#2. Mine minerals
#*3. Follow instructions
#*3. Trace Map
#*4. Explore map efficiently
# 5. Seek unvisited vertexes
# 6. Return to Deployment zone

    tick = 0
    def __init__(self, overlord):
        self.instructionQueue = []
        self.mapId = 0
        self.overlord = overlord
        self.location = (0, 0)
        self.home = (0, 0)
        self.returnMode = False
        self.HP = 20
        self.mineralsMined = 0
        self.graph = None

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

    def move_to_point(self, context, point):
        if self.location[0] > point[0] and context.west in ' _~*':
            return 'WEST'
        elif self.location[0] < point[0] and context.east in ' _~*':
            return 'EAST'
        elif self.location[1] > point[1] and context.south in ' _~*':
            return 'SOUTH'
        elif self.location[1] < point[1] and context.north in ' _~*':
            return 'NORTH'
        else:
            return 'CENTER'

    def focus_minerals(self, context):
        if context.north in '*':
            self.mineralsMined += 1
            return 'NORTH'
        elif context.south in '*':
            self.mineralsMined += 1
            return 'SOUTH'
        elif context.east in '*':
            self.mineralsMined += 1
            return 'EAST'
        elif context.west in '*':
            self.mineralsMined += 1
            return 'WEST'
        else:
            return False

    def add_instruction_set(self, instructionList):
        self.instructionQueue.insert(0, instructionList)
        # Flatten list
        self.instructionQueue = [y for x in self.instructionQueue for y in x]
    
    def follow_instruction(self, context):
        if self.location == self.instructionQueue[0]:
            self.instructionQueue.pop(0)

        if self.instructionQueue:
            direction = self.move_to_point(context, self.instructionQueue[0])
            if direction == 'NORTH':
                return 'NORTH'
            elif direction == 'SOUTH':
                return 'SOUTH'
            elif direction == 'EAST':
                return 'EAST'
            elif direction == 'WEST':
                return 'WEST'
            else:
                return 'CENTER'
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

    def update_graph(self, context):
        #TODO:  Just pass it the context, and have it create vertexes that have
        #           not been visisted
        x = context.x
        y = context.y
        #North update
        self.graph.addEdge((x, y), (x, y+1), context.north )
        #South update
        self.graph.addEdge((x, y), (x, y-1), context.south )
        #East update
        self.graph.addEdge((x, y), (x+1, y), context.east )
        #West update
        self.graph.addEdge((x, y), (x-1, y), context.west )

    def seek_unvisited(self, context):
        x = context.x
        y = context.y
        if self.graph.vertList[(x,y+1)].visited == False:
            if context.north == ' ':
                return 'NORTH'
        if self.graph.vertList[(x,y-1)].visited == False:
            if context.south == ' ':
                return 'SOUTH'
        if self.graph.vertList[(x+1, y)].visited == False:
            if context.east == ' ':
                return 'EAST'
        if self.graph.vertList[(x-1, y)].visited == False:
            if context.west == ' ':
                return 'WEST'

    def request_route(self, start, finish):
        self.overlord.generate_route(self, start, finish)


    def move(self, context):
        self.update_graph(context)

        self.location = (context.x, context.y)

        if self.returnMode == True:
            #route = a_star_search(self.graph, self.location, self.home)
            #print(route)
            #input()

            if self.instructionQueue:
                direction = self.follow_instruction(context)
            else:
                self.request_route(self.location, self.home)
                direction = self.follow_instruction(context)

            if direction == 'CENTER':
                #Calls to Overlord to let it know, it's at deployment area
                self.overlord.return_zerg(self)
                #TODO: Make it a Overlord method, when the overlord actually picks
                #       the drone up
                self.mineralsMined = 0
                return direction
            elif direction:
                return direction

        elif self.home[0] == 0 and self.home[1] == 0:
            self.home = (context.x, context.y)
            return self.leave_deployment_zone(context)

        direction = self.focus_minerals(context)
        if direction:
            return direction

        if self.instructionQueue:
            direction = self.follow_instruction(context)
            if direction:
                return direction

        direction = self.seek_unvisited(context)
        if direction:
            return direction

        direction = self.random_direction(context)
        if direction and self.returnMode == False:
            return direction

        return 'CENTER'



class Overlord:
    def __init__(self, ticks):
        self.maps = {}
        self.zerg = {}
        self.graphs = {}
        self.zergDropList = []
        self.nextMap = 0
        self.zergReturnList = []
        self.ticksLeft = ticks
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

    def get_graph(self, mapId):
        return self.graphs.get(mapId, None)

    def generate_route(self, drone, location, goal):
        route = a_star_search(drone.graph, location, goal)
        drone.add_instruction_set(route)
        
            
        
 
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
            # Creating graph
            graph = self.graphs.get(mapId, None)
            if graph:
                self.zerg[zerg].graph = graph
            else:
                self.graphs[mapId] = Graph()
                self.zerg[zerg].graph = self.graphs[mapId]
            return 'DEPLOY {} {}'.format((zerg), mapId)

        else:
            if self.returningDrones == True:
                return 'RETURN {}'.format(choice(list(self.zerg.keys())))
            else:
                return 'DEPLOY {} {}'.format(choice(list(self.zerg.keys())),
                    choice(list(self.maps.keys())))

        


