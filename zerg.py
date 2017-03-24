#!/usr/local/bin/python
from graph import Vertex, Graph
from astar import *
from random import randint, choice
from maptracker import MapTracker

"""
    
"""
class Drone:
    droneCount = 0

    def __init__(self, overlord):
        self.instructionQueue = []
        self.zergId = Drone.droneCount
        Drone.droneCount += 1
        self.mapId = 0
        self.overlord = overlord
        self.location = (0, 0)
        self.home = (0, 0)
        self.returnMode = False
        self.hp = 40
        self.mineralsMined = 0
        self.graph = None
        self.wallMode = True


    def update_graph(self, context):
        #TODO:  Just pass it the context, and have it create vertexes that have
        #           not been visisted
        x = context.x
        y = context.y
        # North update
        self.graph.addEdge((x, y), (x, y+1), context.north )
        # South update
        self.graph.addEdge((x, y), (x, y-1), context.south )
        # East update
        self.graph.addEdge((x, y), (x+1, y), context.east )
        # West update
        self.graph.addEdge((x, y), (x-1, y), context.west )


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


    def find_wall(self, context):
        if self.zergId % 2 == 0:
            if context.west == '#':
                self.wallMode == False
                return 'CENTER'
            elif context.west in ' _':
                return 'WEST'
            elif context.west in '~Z':
                return choice(['NORTH','SOUTH'])
        else:
            if context.east == '#':
                self.wallMode == False
                return 'CENTER'
            elif context.east in ' _':
                return 'EAST'
            elif context.west in '~Z':
                return choice(['NORTH', 'SOUTH'])

        return None


    def random_direction(self, context): 
        new = randint(0, 3)
        if new == 0 and context.north in ' _':
            return 'NORTH'
        elif new == 1 and context.south in ' _':
            return 'SOUTH'
        elif new == 2 and context.east in ' _':
            return 'EAST'
        elif new == 3 and context.west in ' _':
            return 'WEST'
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


    def purge_instruction(self):
        self.instructionQueue = []


    def add_instruction_set(self, instructionList):
        for instruction in reversed(instructionList):
            self.instructionQueue.insert(0, instruction)


    def follow_instruction(self, context):
        if self.instructionQueue:
            if self.location == self.instructionQueue[0]:
                self.instructionQueue.pop(0)
        else:
            return 'CENTER'
        
        if self.instructionQueue:
            instruction = self.instructionQueue[0]
            vertex = self.graph.vertList[instruction]
        else:
            return 'CENTER'


        if vertex.symbol in '#~':
            self.purge_instruction()
            return self.random_direction(context)

        if vertex.symbol in 'Z':
            if self.returnMode == True:
                self.purge_instruction()
            return self.random_direction(context)

        if self.instructionQueue:
            direction = self.move_to_point(context, instruction)
            if direction == 'NORTH':
                if context.north == '~':
                    self.hp -= 3
                return 'NORTH'
            elif direction == 'SOUTH':
                if context.south == '~':
                    self.hp -= 3
                return 'SOUTH'
            elif direction == 'EAST':
                if context.east == '~':
                    self.hp -= 3
                return 'EAST'
            elif direction == 'WEST':
                if context.west == '~':
                    self.hp -= 3
                return 'WEST'
            else:
                return 'CENTER'
        else:
            return 'CENTER'


    def uncover_neighbor(self, context):
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


    def return_home(self, context):
        #route = a_star_search(self.graph, self.location, self.home)
        #print(route)
        #input()
        if self.location == self.home:
            #Calls to Overlord to let it know, it's at deployment area
            self.overlord.return_zerg(self)
            #TODO: Make it a Overlord method, when the overlord actually picks
            #       the drone up
            return 'CENTER'        

        if self.instructionQueue:
            direction = self.follow_instruction(context)
        else:
            self.request_route(self.location, self.home)
            direction = self.follow_instruction(context)

        return direction


    def visit_unvisited(self, context):
        if self.instructionQueue:
            direction = self.follow_instruction(context)
        else:
            self.overlord.return_unvisited(self)
            direction = self.follow_instruction(context)

        return direction


    def move(self, context):
        self.update_graph(context)
        self.location = (context.x, context.y)

        if self.returnMode == True:
            direction = self.return_home(context)
            if direction:
                return direction

        elif self.home[0] == 0 and self.home[1] == 0:
            self.home = (context.x, context.y)
            return self.leave_deployment_zone(context)

        direction = self.focus_minerals(context)
        if direction:
            return direction

        if self.wallMode == True:
            direction = self.find_wall(context)
            if direction:
                if direction == 'CENTER':
                    self.wallMode = False
                return direction

        direction = self.uncover_neighbor(context)
        if direction:
            return direction

        direction = self.visit_unvisited(context)
        if direction:
            return direction

        if self.return_mode == True:
            return self.move_to(context, self.home)
        else:
            return self.random_direction(context)


class Overlord:
    def __init__(self, ticks):
        self.maps = {}
        self.zerg = {}
        self.graphs = {}
        self.zergDropList = []
        self.zergReturnList = []
        self.ticks = ticks
        self.ticksLeft = ticks
        self.noMoreDeployment = False

        nextMap = 0
        for number in range(6):
            z = Drone(self)
            self.zergDropList.append(z)
            self.zerg[id(z)] = z

            mapId = nextMap
            nextMap += 1
            if nextMap > 2:
                nextMap = 0
            z.mapId = mapId

    # Function used to determined the mininum number of changes required to
    #   go from one coordinate to another
    def determine_distance(self, pair1, pair2):
        return abs(pair1[0] - pair2[0]) + abs(pair1[1] - pair2[1])

    def add_map(self, map_id, summary):
        self.maps[map_id] = summary

    def return_zerg(self, zergObject):
        if zergObject in self.zergReturnList:
            pass
        else:
            self.zergReturnList.append(zergObject)

    def get_graph(self, mapId):
        return self.graphs.get(mapId, None)

    def return_unvisited(self, drone):
        route = None
        goal = None
        goal = first_unvisited(drone.graph, drone.location)
        try:
            drone.graph.vertList[goal].visited = True
            route = a_star_search(drone.graph, drone.location, goal, drone.hp)
        except:
            pass
        drone.purge_instruction()
        if route:
            drone.add_instruction_set(route)

    def generate_route(self, drone, location, goal):
        route = a_star_search(drone.graph, location, goal, drone.hp)
        drone.purge_instruction()
        drone.add_instruction_set(route)

    def check_to_return(self):
        for zerg in self.zerg.items():
            zerg = zerg[1]
            distance = self.determine_distance(zerg.location, zerg.home)
            if distance > self.ticksLeft - 50:
                self.noMoreDeployment = True
                zerg.returnMode = True
            if zerg.mineralsMined >= 10 and zerg.returnMode == False:
                zerg.returnMode = True

    def check_for_wallMode(self):
        for zerg in self.zerg.items():
            zerg = zerg[1]
            if zerg.wallMode == True:
                if self.ticks - self.ticksLeft > 30:
                    zerg.wallMode = False

    def action(self):
        self.ticksLeft -= 1

        self.check_for_wallMode()
        self.check_to_return()

        if self.zergReturnList:
            zerg = self.zergReturnList.pop(0)
            if self.noMoreDeployment == False:
                self.zergDropList.append(zerg)
            return 'RETURN {}'.format(id(zerg))

        elif self.zergDropList:
            zerg = self.zergDropList.pop(0)


            graph = self.graphs.get(zerg.mapId, None)
            if graph:
                zerg.graph = graph
            else:
                self.graphs[zerg.mapId] = Graph(zerg.mapId)
                zerg.graph = self.graphs[zerg.mapId]
            zerg.mineralsMined = 0
            zerg.returnMode = False
            return 'DEPLOY {} {}'.format((id(zerg)), zerg.mapId)

        else:
            if self.noMoreDeployment == True:
                return 'RETURN {}'.format(choice(list(self.zerg.keys())))
            else:
                zergID = choice(list(self.zerg.keys()))
                return 'DEPLOY {} {}'.format(zergID, self.zerg[zergID].mapId)

        


