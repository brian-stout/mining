# Implementation modified from
# http://www.redblobgames.com/pathfinding/a-star/implementation.html


import heapq


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


def heuristic(a, b):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    return abs(x1 - x2) + abs(y1 - y2)


def a_star_search(graph, start, goal, hp):

    queue = PriorityQueue()
    queue.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not queue.empty():
        current = queue.get()

        if current == goal:
            break

        # TODO: Automatically generate neighbors as we search for to
        #       create a straighter path
        for next in graph.vertList[current].connectedTo:
            next = next.id
            weight = 1
            if graph.vertList[current].symbol == '~' and hp < 10:
                weight = 9999
            elif graph.vertList[current].symbol == '~':
                weight = 10
            elif graph.vertList[current].symbol in '#':
                weight = 9999
            new_cost = cost_so_far[current] + weight
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                queue.put(next, priority)
                came_from[next] = current

    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    path.append(start)
    path.reverse()

    path.pop(0)
    return path


def first_unvisited(graph, start):
    queue = PriorityQueue()
    queue.put(start, 0)
    visited = {}
    visited[start] = True

    while not queue.empty():
        current = queue.get()
        for next in graph.vertList[current].connectedTo:
            next = next.id
            if graph.vertList[next].visited is False:
                return next
            if next not in visited:
                queue.put(next, 0)
                visited[next] = True

    return None
