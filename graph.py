# Code modified from
# http://interactivepython.org/courselib/
# static/pythonds/Graphs/Implementation.html

"""
    class Vertex:

    The vertex object is based on a location.  The key is a tuple of
        a x and a y.

    The vertex object also contains a dictionary of
        of neighboring vertexes (the key's are also a tuple)
        as well as the symbol of the neighbor if it's known
"""


class Vertex:
    def __init__(self, key, symbol):
        self.id = key
        self.symbol = symbol
        self.connectedTo = {}
        self.visited = False

    # Used to add adjacent nodes that have been discovered
    def add_neighbor(self, neighbor):
        self.connectedTo[neighbor] = neighbor.symbol

    def __str__(self):
        connectedTo = str([x.id for x in self.connectedTo])
        return str(self.id + ' connectedTo: ' + connectedTo)

    def get_connections(self):
        return self.connectedTo.keys()

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.connectedTo[neighbor]

"""
    class Graph:

    The graph class creates an object that tracks all the vertexes
        that have been discovered by a drone for a specific map and how it
        it connects to other vertexes using vertex class objects
"""


class Graph:
    def __init__(self, mapId):
        self.vertList = {}
        self.numVertices = 0
        self.highestX = 0
        self.highestY = 0
        self.mapId = mapId
        self.mineralsMined = 0
        self.complete = False

    def add_vertex(self, key, symbol):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex(key, symbol)
        self.vertList[key] = newVertex
        return newVertex

    """
    method get_vertex
    """
    def get_vertex(self, n):
        if n in self.vertList:
            return self.vertList[n]
        else:
            return None

    def __contains__(self, n):
        return n in self.vertList

    # TODO: Add so it just takes a fromVertex Key and a context, and updates it
    #       in the function instead of multiple function calls in Drone
    # TODO: Automatically generate neighbors based on coordinates
    #        and default populate with 'X'

    def add_edge(self, fromVertex, toVertex, symbol):
        # Checks to see if the new vertex has neighbors that increase
        #   the bounds of the map.  This is used for the __str__method
        if toVertex[0] > self.highestX:
            self.highestX = toVertex[0]
        if toVertex[1] > self.highestY:
            self.highestY = toVertex[1]

        # If vertex is none existent, add it
        if fromVertex not in self.vertList:
            newVertex = self.add_vertex(fromVertex, 'Z')
            newVertex.visited = True
        # If it does exist, update it's current value
        else:
            self.vertList[fromVertex].symbol = 'Z'
            self.vertList[fromVertex].visited = True
        # If vertex is none existent, add it
        if toVertex not in self.vertList:
            newVertex = self.add_vertex(toVertex, symbol)
        else:
            self.vertList[toVertex].symbol = symbol
            # If it's something the drone can't occupy, set visited
            #   to true
            if symbol in '#~':
                self.vertList[toVertex].visited = True
        # Calls on the fromVertex's addNeight method, and adds the to vertex
        self.vertList[fromVertex].add_neighbor(self.vertList[toVertex])

    def getVertices(self):
        return self.vertList.keys()

    # Method used for printing out all the edge connections
    #   mostly for testing purposes
    def print_edge_data(self):
        if self.vertList:
            for v in self:
                for w in v.get_connections():
                    formS = "(%s%s, %s%s)"
                    print(formS % (v.get_id(), v.symbol, w.get_id(), w.symbol))
        print()

    # Method called by drone to add to the mineral count of a graph
    def add_minerals(self, count):
        self.mineralsMined += count
        self.check_if_complete()

    # TODO: Add code to detect the amount of minerals on a map
    #   based on the map summary and the size of the map
    def check_if_complete(self):
        return self.complete

    def __iter__(self):
        return iter(self.vertList.values())

    # Method used to print a physical representation of the map when
    #   the graph is printed.
    #
    # Any vertex called that does not provide back symbol data
    #   defaults to an 'X' as an unexplored area
    def __str__(self):
        returnString = ''
        for y in reversed(range(self.highestY+1)):
            line = ''
            for x in range(self.highestX+1):
                vertex = self.vertList.get((x, y), None)
                if vertex:
                    line += vertex.symbol
                else:
                    line += 'X'
            line += '\n'
            returnString += line
        return returnString
