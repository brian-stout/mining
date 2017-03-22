#Code modified from http://interactivepython.org/courselib/static/pythonds/Graphs/Implementation.html

class Vertex:
    def __init__(self, key, symbol):
        self.id = key
        self.symbol = symbol
        self.connectedTo = {}
        if symbol == '#':
            self.terminus = True
        else:
            self.terminus = False

    def addNeightbor(self, neighbor):
        self.connectedTo[neighbor] = neighbor.symbol

    def __str__(self):
        return str(self.id) + ' connectedTo: ' + str([x.id for x in self.connectedTo])

    def getConnections(self):
        return self.connectedTo.keys()
    
    def getId(self):
        return self.id
    
    def getWeight(self, neighbor):
        return self.connectedTo[neighbor]

class Graph:
    def __init__(self):
        self.vertList = {}
        self.numVertices = 0
        self.highestX = 0
        self.highestY = 0

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

    #TODO: Add so it just takes a fromVertex Key and a context, and updates it
    #       in the function instead of multiple function calls in Drone
    def addEdge(self, fromVertex, toVertex, symbol):
        if toVertex[0] > self.highestX:
            self.highestX = toVertex[0]
        if toVertex[1] > self.highestY:
            self.highestY = toVertex[1]

        # If vertex is none existent, add it
        if fromVertex not in self.vertList:
            newVertex = self.addVertex(fromVertex, 'Z')
        # If it does exist, update it's current value
        else:
            self.vertList[fromVertex].symbol = 'Z'
        # If vertex is none existent, add it
        if toVertex not in self.vertList:
            newVertex = self.addVertex(toVertex, symbol)
        else:
            self.vertList[toVertex].symbol = symbol
        # Calls on the fromVertex's addNeight method, and adds the to vertex
        self.vertList[fromVertex].addNeightbor(self.vertList[toVertex])
        #self.vertList[toVertex].addNeightbor(self.vertList[fromVertex])

    def getVertices(self):
        return self.vertList.keys()

    def print_edge_data(self):
        if self.vertList:
            for v in self:
                for w in v.getConnections():
                    formatS = "(%s%s, %s%s)"
                    print( formatS % (v.getId(), v.symbol, w.getId(), w.symbol))
        print()

    def __iter__(self):
        return iter(self.vertList.values())

    def __str__(self):
        returnString = ''
        for y in reversed(range(self.highestY)):
            line = ''
            for x in range(self.highestX):
                vertex = self.vertList.get((x, y), None)
                if vertex:
                    line += vertex.symbol
                else:
                    line += 'X'
            line += '\n'
            returnString += line
        return returnString
                
        
