# Code modified from
# http://interactivepython.org/courselib/
# static/pythonds/Graphs/Implementation.html


class Vertex:
    def __init__(self, key, symbol):
        self.id = key
        self.symbol = symbol
        self.connectedTo = {}
        self.visited = False
        if symbol == '#':
            self.terminus = True
        else:
            self.terminus = False

    def addNeightbor(self, neighbor):
        self.connectedTo[neighbor] = neighbor.symbol

    def __str__(self):
        connectedTo = str([x.id for x in self.connectedTo])
        return str(self.id + ' connectedTo: ' + connectedTo)

    def getConnections(self):
        return self.connectedTo.keys()

    def getId(self):
        return self.id

    def getWeight(self, neighbor):
        return self.connectedTo[neighbor]


class Graph:
    def __init__(self, mapId):
        self.vertList = {}
        self.numVertices = 0
        self.highestX = 0
        self.highestY = 0
        self.mapId = mapId
        self.mineralsMined = 0
        self.complete = False

    def addVertex(self, key, symbol):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex(key, symbol)
        self.vertList[key] = newVertex
        return newVertex

    def getVertex(self, n):
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

    def addEdge(self, fromVertex, toVertex, symbol):
        if toVertex[0] > self.highestX:
            self.highestX = toVertex[0]
        if toVertex[1] > self.highestY:
            self.highestY = toVertex[1]

        # If vertex is none existent, add it
        if fromVertex not in self.vertList:
            newVertex = self.addVertex(fromVertex, 'Z')
            newVertex.visited = True
        # If it does exist, update it's current value
        else:
            self.vertList[fromVertex].symbol = 'Z'
            self.vertList[fromVertex].visited = True
        # If vertex is none existent, add it
        if toVertex not in self.vertList:
            newVertex = self.addVertex(toVertex, symbol)
        else:
            self.vertList[toVertex].symbol = symbol
            if symbol in '#~':
                self.vertList[toVertex].visited = True
        # Calls on the fromVertex's addNeight method, and adds the to vertex
        self.vertList[fromVertex].addNeightbor(self.vertList[toVertex])

    def getVertices(self):
        return self.vertList.keys()

    def print_edge_data(self):
        if self.vertList:
            for v in self:
                for w in v.getConnections():
                    formatS = "(%s%s, %s%s)"
                    print(formatS % (v.getId(), v.symbol, w.getId(), w.symbol))
        print()

    def add_minerals(self, count):
        self.mineralsMined += count
        self.check_if_complete()

    def check_if_complete(self):
        if self.mineralsMined >= 45:
            self.complete = True
            return True
        else:
            return False

    def __iter__(self):
        return iter(self.vertList.values())

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
