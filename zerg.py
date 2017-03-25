#!/usr/local/bin/python
from mining.graph import Vertex, Graph
from mining.astar import *
from random import randint, choice


"""
    class Drone:

    The drone class substantiates a dumb agent that traverses the map
        given a set of rules.  Which direction it goes is based on several
        methods that govern the logic the drone uses.  These methods are
        ordered by priority so that the method determines if the scenario is
        applicable or not.  If it is, it will determine a direction.  If
        it is not, it won't return one and the Drone will move
        on to the next method.

    The main method in the drone class is the move method, which contains
        the methods ordered by priority.

    The priority list is:
            1. Set home
            2. update_graph (always done)
            3. update the location (always done)
            4. mine nearby minerals
                a. Will not do if the overlord
                    is recalling all the drones
            5. return_home
            6. find_wall
            7. uncover_neighbor
            8. visit_unvisited
            9. Default action

    If no action is taken, the default action is to move closer to home
        if the returnMode has been set to true, else move
        in a random direction. The random direction
        sometimes helps the drone get unstuck.
"""


class Drone:
    droneCount = 0

    def __init__(self, overlord):
        # zergId is used to determine which direction the drone
        #   goes when the find_wall() method is called
        self.zergId = Drone.droneCount
        Drone.droneCount += 1

        # List containing coordinates for drone to follow
        self.instructionQueue = []

        # mapId is assigned when a zerg is deployed to map
        #   and is used most often to call for a map's graph
        #   by the overlord
        self.mapId = 0

        self.overlord = overlord  # parent overlord
        self.location = (0, 0)  # current location

        # the first coordinates received when deployed
        self.home = (0, 0)
        self.returnMode = False  # if true drone will head to home
        self.hp = 40
        self.minerals = 0

        # The graph the drone sends updates to
        self.graph = None
        self.wallMode = True  # if  true drone will seek a wall

    """
    method update_graph():

    When called the drone will send the context it received
        to it's graph which will use the information to create
        connections.

    The graph uses tuples as a key,
        index 0 is the x value
         index 1 is the y value
    """
    def update_graph(self, context):
        x = context.x
        y = context.y
        # North update
        self.graph.add_edge((x, y), (x, y+1), context.north)
        # South update
        self.graph.add_edge((x, y), (x, y-1), context.south)
        # East update
        self.graph.add_edge((x, y), (x+1, y), context.east)
        # West update
        self.graph.add_edge((x, y), (x-1, y), context.west)

    """
    method find_wall():

    The method makes the drone seek the first # symbol
        it can find.  The purpose of this is mostly
        to seperate the two drones when they first enter the map

    The method does this by determining if a zergId has an odd
        or an even Id.  If it is even it heads west, opposite if
        it's east.

    If the drone runs in to an obstacle such as another zerg
        or an acid pool, it will randomly choose up or down
        to avoid it.

    Some situations the drone will still get stuck.
        If after a certain amount of ticks, wallMode is still
        on, the overlord will set it to off and the drone
        will run normal operations from it's location
    """
    def find_wall(self, context):
        if self.zergId % 2 == 0:
            if context.west == '#':
                self.wallMode = False
                return 'CENTER'
            elif context.west in ' _':
                return 'WEST'
            elif context.west in '~Z':
                return choice(['NORTH', 'SOUTH'])
        else:
            if context.east == '#':
                self.wallMode = False
                return 'CENTER'
            elif context.east in ' _':
                return 'EAST'
            elif context.west in '~Z':
                return choice(['NORTH', 'SOUTH'])

        return None

    """
    method random_direction():
        This method just randomly picks a cardinal direction.

        This is mostly used for scenarios where the drone can't resolve
            an obstacle and the normal logic can't get it unstuck

        As a last resort the Drone will just try things, and hopefully
            fix itself
    """
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

    """
    method focus_minerals():
        This method returns a direction of the first mineral object
            it can find.

        If it can't, it will return no direction, and the next method
            will be called.

        focusing on minerals has the top priority, unless the overlord
            is recalling all drones, then returning to home does
    """
    def focus_minerals(self, context):
        if context.north in '*':
            self.minerals += 1
            # Used by graph to determine when all the minerals are
            # collected
            self.graph.mineralsMined += 1
            return 'NORTH'
        elif context.south in '*':
            self.minerals += 1
            self.graph.mineralsMined += 1
            return 'SOUTH'
        elif context.east in '*':
            self.minerals += 1
            self.graph.mineralsMined += 1
            return 'EAST'
        elif context.west in '*':
            self.minerals += 1
            self.graph.mineralsMined += 1
            return 'WEST'
        else:
            return False

    """
    method move_to_point():

    The move_to_point method determines the difference between the
        x,y coordinates of it's current location, and the
        end location.

    When it finds these differences it will move in the direction
        that makes this difference smaller in practice moving
        closer to the goal point every single time

    """
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

    """
    method purge_instruction():

    This method simply sets the instructionQueue to an empty list.

    When the drone determines that a goal is impossible to get to
        or a path is too dangerous to follow, it empty's out the list
        to either grab a new route, or follow basic logic
    """
    def purge_instruction(self):
        self.instructionQueue = []

    """
    method add_instruction():

    This method is used by the overlord to assign a set of instructions
        to the drone
    """
    def add_instruction_set(self, instructionList):
        for instruction in reversed(instructionList):
            self.instructionQueue.insert(0, instruction)

    """
    method uncover_neighbor()

    This method checks to see if any adjacent spots haven't been visited
        If it hasn't then it explores it, since map exploration has
        a high priority in our goals.

    The main use of the method is because the logic to check a neighbor
        is much simpler than the logic to do a graph search for a
        unvisited node.

    An improvement to this method would be if it checked to see which
        neighbor has the largest amounts of unchecked neighbors and
        prioritize this one.  This would lead to a drone carving through
        the map as opposed to doing a scanline and improve search times
    """
    def uncover_neighbor(self, context):
        x = context.x
        y = context.y
        # North neighbor
        if self.graph.vertList[(x, y+1)].visited is False:
            if context.north == ' ':
                return 'NORTH'
        # South neighbor
        if self.graph.vertList[(x, y-1)].visited is False:
            if context.south == ' ':
                return 'SOUTH'
        # East Neighbor
        if self.graph.vertList[(x+1, y)].visited is False:
            if context.east == ' ':
                return 'EAST'
        # West Neighbor
        if self.graph.vertList[(x-1, y)].visited is False:
            if context.west == ' ':
                return 'WEST'

    """
    method follow_instruction():

    The main method of the drone, and the most complicated one.

    When the overlord give a route to the drone it uses this logic
        to follow the orders.
    """
    def follow_instruction(self, context):
        # Determines if a drone has succesfully moved to the next
        # coordinate.  If it has, it pops that instruction of
        if self.instructionQueue:
            if self.location == self.instructionQueue[0]:
                self.instructionQueue.pop(0)
        # if there's no queue to begin with, return none so drone
        #   can use rest of the logic
        else:
            return None

        # Checks to see if the last instruction got popped off
        if self.instructionQueue:
            instruction = self.instructionQueue[0]

            # Grabs the vertex at that coordinate
            vertex = self.graph.vertList.get(instruction, None)

            # Extra check because there's been errors
            #   if it fails to grab, return no direction and purge
            #   since the data is bad somehow
            if vertex is None:
                self.purge_instruction()
                return None
        else:
            return None

        # If the zerg has been ordered to move on a wall or a ~
        #   the route is bad, so purge it and move in a random safe
        #   direction to avoid odd problems
        if vertex.symbol in '#~':
            self.purge_instruction()
            return self.random_direction(context)

        # If the zerg has been ordered to move on another zerg
        #   skip this turn and move in a random_direction to attempt
        #   to avoid another collision with the zerg
        # If the returnMode is on, purge the route since the overlord
        #   will just give a new one
        if vertex.symbol in 'Z':
            if self.returnMode is True:
                self.purge_instruction()
            return self.random_direction(context)

        if self.instructionQueue:
            # Call move_to_point to get a direction that gets the drone
            #   closer to the next coordinate
            # The move_to_point function is used if a drone gets offset
            #   or if waypoints are eventually added
            direction = self.move_to_point(context, instruction)
            if direction == 'NORTH':
                # Before returning direction, check if moving in acid
                # If yes, then decrement the drones HP
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

        # IF, all these checks fail to return a direction, just hope
        #   nothing is too bad and pick a random direction
        else:
            return self.random_direction(context)

    """
    method request_route():

    The request_route method calls to the overlord to receive
        a route to the specified goal.  This is always the home
        or an unvisited node
    """
    def request_route(self, start, finish):
        self.overlord.generate_route(self, start, finish)

    """
    method return_home():

    The return_home() method is called when a drone's returnMode
        is set to true.  It's purpose is to get the drone back
        to it's deployment area.

    When the drone is at the deployment area, it'll call to the
        overlord that it's ready for a pickup
    """
    def return_home(self, context):
        if self.location == self.home:
            # Calls to Overlord to let it know, it's at deployment area
            self.overlord.return_zerg(self)
            return 'CENTER'  # Keeps drone on deployment area

        # If drone already has instructions to home
        #   follow them
        # When a drone is first set to return mode, it purges
        #   it's current instructionQueue
        if self.instructionQueue:
            direction = self.follow_instruction(context)
        # If there is none, request one, then follow that direction
        else:
            self.request_route(self.location, self.home)
            direction = self.follow_instruction(context)

        return direction

    """
    method visit_unvisited():

    This method calls up the overlords return_unvisited method.

    This method returns a set of instructions to the nearest node
        that hasn't been visited by a drone

    Upon requesting the current instruction list is purged
    """
    def visit_unvisited(self, context):
        # If there are already instructions follow them
        if self.instructionQueue:
            direction = self.follow_instruction(context)
        # Request directions if instructionQueue is empty
        else:
            self.overlord.return_unvisited(self)
            direction = self.follow_instruction(context)

        return direction

    """
    method move():

    The main method handles which movement method to use.

    The main logic is that it attempts a method, and if the method
        returns no direction because it's not applicable,
        it will return no direction so it'll move on to the next
        one.

    It's used by the driver program to move the drone.

    """
    def move(self, context):
        # The first move we set the home to where the zerg was deployed
        # If home is 0,0 (an impossible coordinate to get to,)
        #   then the first context location we get is set to the home
        #   before the drone can move
        if self.home[0] == 0 and self.home[1] == 0:
            self.home = (context.x, context.y)
            self.graph.home = self.home

        # Always update the graph when you can
        self.update_graph(context)

        # Update the drone's location
        self.location = (context.x, context.y)

        # If a overlord isn't recalling drones, focus on minerals
        #   if it is, then ignore them
        if self.overlord.noMoreDeployment is False:
            direction = self.focus_minerals(context)
            if direction:
                return direction

        # If a drone is set to go to the deployment zone
        #   run the return_home method to get there
        if self.returnMode is True:
            direction = self.return_home(context)
            if direction:
                return direction

        # Seeks the first wall block using the find_wall method
        if self.wallMode is True:
            direction = self.find_wall(context)
            if direction:
                if direction == 'CENTER':
                    self.wallMode = False
                return direction

        # Checks the adjacent vertexes for an unvisited vertex
        #   and goes to it
        direction = self.uncover_neighbor(context)
        if direction:
            return direction

        # If all neighboring vertexes are visited, find the next closest
        #   vertex
        direction = self.visit_unvisited(context)
        if direction:
            return direction

        # Default options
        #   if the returnMode is true, attempt to move closer to deployment
        if self.returnMode is True:
            return self.move_to_point(context, self.home)
        #   If it's not, just move for the sake of moving
        else:
            return self.random_direction(context)

"""
    class Overlord:

    The overlord class creates an object whose purpose is to
        handle the heavy logic operations related to the drone
        path finding, as well as the logic dictating how to use
        the drones entirely.

    This means that drones can request routes from the overlord, and
        the overlord handles logic for deploying and returning drones
"""


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
        # Creates all six drones and adds them to the drop list
        for number in range(6):
            z = Drone(self)
            self.zergDropList.append(z)
            self.zerg[id(z)] = z

            # Assigns a mapId to the zerg
            # Used to deploy only two zerg to one map
            #   initially
            mapId = nextMap
            nextMap += 1
            if nextMap > 2:
                nextMap = 0
            z.mapId = mapId

    # Function used to determined the mininum number of moves required to
    #   go from one coordinate to another
    def determine_distance(self, pair1, pair2):
        return abs(pair1[0] - pair2[0]) + abs(pair1[1] - pair2[1])

    # Provided code
    def add_map(self, map_id, summary):
        self.maps[map_id] = summary

    """
    method return_zerg():

    This method is called by a drone when it's returning
        and on the deployment zone.

    It add the drone to the returnList so the overlord
        will call to return it.
    """
    def return_zerg(self, zergObject):
        if zergObject in self.zergReturnList:
            pass
        else:
            self.zergReturnList.append(zergObject)

    """
    method return_unvisited():

    Runs a breadth first search from the drone's location looking
        for the first unvisited node.

    After it finds the first unvisited node, this function provides a
        route using A* pathfinding to the zerg.
    """
    def return_unvisited(self, drone):
        route = None
        goal = None
        # Grab the coordinates of the nearest unvisited node
        goal = first_unvisited(drone.graph, drone.location)
        # Try block because somtimes there's weird index errors
        try:
            # When returned, set it to true so it's not visited again
            drone.graph.vertList[goal].visited = True
            # Make a route from current location to the unvisited node
            route = a_star_search(drone.graph, drone.location, goal, drone.hp)
        except:
            pass
        # Purge the instructions
        drone.purge_instruction()
        # If a route was found, add it to the drone's instruction Queue
        if route:
            drone.add_instruction_set(route)

    """
    method generate_route():

    This method given a drone, it's location, and an end goal,
        will call on the a_star_search to find a route to the goal
    """
    def generate_route(self, drone, location, goal):
        route = a_star_search(drone.graph, location, goal, drone.hp)
        drone.purge_instruction()
        drone.add_instruction_set(route)

    """
    method check_to_return():

    This method is run at the start of every overlord action to check
        if a drone should be returned to the deployment zone
    """
    def check_to_return(self):
        # Checking every zerg it's in charge of
        for zerg in self.zerg.items():
            # Provided code gives a tuple for some reason
            #   second index is the zerg object
            zerg = zerg[1]
            distance = self.determine_distance(zerg.location, zerg.home)
            # Default graphSize, it's used as a extra reassurance that
            #   The drone will have enough ticks to return home
            # The larger the map the greater the extra room
            graphSize = 15

            # Sometimes the zerg doesn't have graph, so check first
            if zerg.graph:
                # Determine extra room based on map size
                graphSize = zerg.graph.highestX + zerg.graph.highestY

            # If the distance is greater than the ticksleft minus the
            #   extraroom, recall the drone
            if distance > self.ticksLeft - graphSize:
                self.noMoreDeployment = True
                zerg.returnMode = True
            # If a zerg has 10 or more minerals, seek deployment zone
            #   this is suboptimal, but ensures zerg will still return
            #   minerals on the off chance it dies
            if zerg.minerals >= 10 and zerg.returnMode is False:
                zerg.returnMode = True
            # Have to check for graph first because a drone
            #   doesn't have a graph Till it's deployed.
            if zerg.graph:
                # If the map is fully checked, go ahead and return the zerg
                if zerg.graph.check_if_complete():
                    zerg.returnMode = True

    """
    method check_for_wallMode():

    After a certain number of ticks, overlord checks each drone to make
        sure the drone isn't still trying to find the wall (is probably stuck)

    If it is, it sets it to off so the drone can move on with it's life
    """
    def check_for_wallMode(self):
        for zerg in self.zerg.items():
            zerg = zerg[1]
            if zerg.wallMode is True:
                if self.ticks - self.ticksLeft > 100:
                    zerg.wallMode = False

    """
    method change_map_id():

    This method is used to change all relevant data on a drone to
        move it to another map.
    """
    def change_map_id(self, zerg):
        mapList = []
        # Grab all the maps that aren't complete yet
        for mapId in self.maps:
            if self.graphs[mapId].complete is False:
                mapList.append(mapId)
        # If there was a found map, grab it
        if mapList:
            mapId = choice(mapList)  # random pick
            zerg.mapId = mapId  # Change the mapId to the new one
            # Sets the home to 0,0 so the drone gets the right home coordinates
            #   next time it's deployed
            zerg.home = (0, 0)
        else:
            self.noMoreDeployment = True

    """
    method action():

    The main method for the overlord object.  This method is called
        by the driver program to simulate a tick

    It handles how the overlord chooses to deploy and return zergs
    """
    def action(self):
        self.ticksLeft -= 1

        self.check_for_wallMode()
        self.check_to_return()

        # Checks if there's zerg waiting to be returned
        if self.zergReturnList:
            # Adds them to the deployment list so they can
            #   be redeployed to same map or another one
            zerg = self.zergReturnList.pop(0)
            # Prevents drones from being redeployed if ticks
            #   are super low
            if self.noMoreDeployment is False:
                self.zergDropList.append(zerg)
            # Returns a string that the driver program uses
            return 'RETURN {}'.format(id(zerg))

        # Checks if there's zergs waiting to be deployed
        elif self.zergDropList:
            zerg = self.zergDropList.pop(0)

            # Attempts to get a graph from the appropiate map
            graph = self.graphs.get(zerg.mapId, None)
            if graph:
                zerg.graph = graph
            # If it can't one needs to be made
            else:
                self.graphs[zerg.mapId] = Graph(zerg.mapId)
                zerg.graph = self.graphs[zerg.mapId]
            # After being deployed reset minerals
            zerg.minerals = 0
            # Make sure the returnMode is false to avoid
            #   It just trying to go back to the deployment zone
            zerg.returnMode = False

            # If a zerg's current map is complete, find a new one
            if zerg.graph.complete is True:
                self.change_map_id(zerg)

            return 'DEPLOY {} {}'.format((id(zerg)), zerg.mapId)

        # The default options in case things go wrong
        else:
            # If all drones have been asked to recall
            #   only attempt to return random zerg Ids
            if self.noMoreDeployment is True:
                return 'RETURN {}'.format(choice(list(self.zerg.keys())))
            # Attempt to deploy a random zerg, in case the initial deployment
            #   failed.
            else:
                zergId = choice(list(self.zerg.keys()))
                if self.zerg[zergId].graph.complete is False:
                    mapId = self.zerg[zergId].mapId
                    return 'DEPLOY {} {}'.format(zergId, mapId)
                else:
                    return 'PASS'

        return 'PASS'
