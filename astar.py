# Implementation modified from
# http://www.redblobgames.com/pathfinding/a-star/implementation.html


import heapq

"""
    class PriorityQueue:
        Creates a basic priority queue structure.  Code was modified
        from the above website.  Is used during the A* pathfinding
        algorithm
"""


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

"""
    function heuristic():

    Function determines the distance between two different coordinates
"""


def heuristic(a, b):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    return abs(x1 - x2) + abs(y1 - y2)

"""
    function a_star_search():

    This function is responsible for finding the shortest path
        between two points and returning the route to them
"""


def a_star_search(graph, start, goal, hp):

    queue = PriorityQueue()
    queue.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not queue.empty():
        current = queue.get()

        # If met destination, break the loop
        if current == goal:
            break

        # TODO: Automatically generate neighbors as we search for to
        #       create a straighter path

        # Grab all the neighbors from the current vertex
        for next in graph.vertList[current].connectedTo:
            # Grab the coordinate data from the object
            next = next.id
            weight = 1
            # If a zerg's hp is low enough, avoid acid at all costs
            if graph.vertList[current].symbol == '~' and hp < 10:
                weight = 9999
            # Otherwise, just make an attempt to avoid
            elif graph.vertList[current].symbol == '~':
                weight = 10
            # if the neighbor is a wall, avoid at all costs
            elif graph.vertList[current].symbol in '#':
                weight = 9999

            # Add the cost so the priority queue prioritizes appropiately
            new_cost = cost_so_far[current] + weight
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                queue.put(next, priority)
                came_from[next] = current

    current = goal
    path = [current]

    # Goes through the data piecing together the route taken for
    while current != start:
        current = came_from[current]
        path.append(current)
    path.append(start)
    # reverses it so the drone can pop the initial path
    path.reverse()

    # Pop the first value since it'll be a duplicate of the start
    path.pop(0)
    return path

"""
    function first_unvisited():

    Performs a breadth first search from the starting point and returns
        the first unvisited vertex it finds
"""


def first_unvisited(graph, start):
    # A normal queue can be used, but there's no point in writing
    #   a more simple data structure
    queue = PriorityQueue()
    queue.put(start, 0)

    # Keep track of vertexes we've seen to avoid loop
    visited = {}

    # Ignores the node we start from
    visited[start] = True

    # Traverses through each of the node's neighbors, and their neighbors, and
    #   so on
    while not queue.empty():
        current = queue.get()
        for next in graph.vertList[current].connectedTo:
            next = next.id
            # If the visited status is false, return it
            if graph.vertList[next].visited is False:
                return next
            if next not in visited:
                queue.put(next, 0)
                visited[next] = True

    # If a graph can not return an unvisited node, then it is fully explored
    graph.complete = True
    return None
