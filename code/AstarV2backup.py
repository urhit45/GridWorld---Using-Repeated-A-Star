import random
import threading
import math
from queue import Queue

try:
    from _queue import Empty
except ImportError:
    class Empty(Exception):
        'Exception raised by Queue.get(block=0)/get_nowait().'
        pass

# Node class for storing position, cost and heuristic for each grid encountered
class Node:
    # Initialize the class
    def __init__(self, position=None, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    # Compare nodes
    def __eq__(self, other):
        return self.position == other.position

    def __hash__(self):
        # hash(custom_object)
        return hash((self.position, self.parent))

    # Print node
    def __repr__(self):
        return ('({0},{1})'.format(self.position, self.f))

    #This returns the neighbours of the Node
    def get_neigbours(self):
        neighbour_cord = [(-1, 0),(0, -1),(0, 1),(1, 0)]
        current_x = self.position[0]
        current_y = self.position[1]
        neighbours = []
        for n in neighbour_cord:
            x = current_x + n[0]
            y = current_y + n[1]
            if 0 <= x < len(matrix) and 0 <= y < len(matrix):
                c = Node()
                c.position = (x, y)
                c.parent = self
                neighbours.append(c)
        return neighbours
    

#Priority Queue to store the nodes and arrange them in increasing order of the total cost (current cost + heuristic cost)
class PriorityQueue:
  
  def __init__(self):
    self.queue = list()
    self.mutex = threading.Lock()
    self.not_empty = threading.Condition(self.mutex)

    # Notify not_full whenever an item is removed from the queue;
    # a thread waiting to put is notified then.
    self.not_full = threading.Condition(self.mutex)

    # Notify all_tasks_done whenever the number of unfinished tasks
    # drops to zero; thread waiting to join() is notified to resume
    self.all_tasks_done = threading.Condition(self.mutex)
    self.unfinished_tasks = 0
    
    
  def insert(self, node,priority):
    # if queue is empty
    if self.size() == 0:
      # add the new node
      self.queue.append(node)
    else:
      # traverse the queue to find the right place for new node
      for x in range(0, self.size()):
        # if the heuristic of new node is greater than equal to the ones in queue then traverse down
        if node.f >= self.queue[x].f:
          # if we have traversed the complete queue
          if x == (self.size()-1):
            # add new node at the end
            self.queue.insert(x+1, node)
          else:
            continue
        else:
          self.queue.insert(x, node)
          return True
  
  def get(self):
    # remove the first node from the queue
    return self.queue.pop(0)
    
  def show(self):
    for x in self.queue:
      print (str(x.position)+" - "+str(x.f))
  
  def size(self):
    return len(self.queue)

  def empty(self):
      with self.mutex:
            return not self.size()

#creating a randomized grid world
def create_grid(n):
    matrix = [ [ 0 for i in range(n) ] for j in range(n) ]
    
    p = 0.75
    for i in range(n):
        for j in range(n):
            if (i == 0 and j == 0) or (i==n-1 and j==n-1):
                matrix[i][j] = 0
            else:
                prob = random.uniform(0, 1)
                if prob >= p:
                    matrix[i][j] = 1
                else:
                    matrix[i][j] = 0
    return matrix

#print the gridworld/knowledge
def print_grid(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            print(matrix[i][j], end=" ")
        print("")

def calc_manhattan(a,b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def calc_euclidean(a,b):
    return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

def calc_chebyshev(a,b):
    return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

def astar(knowledge_grid,start,end):
    grid_len = len(knowledge_grid)
    # Initialize a priority queue
    pQueue = PriorityQueue()
    pQueue.insert(start,0)
    # closed = []
    closed_hash = {}    
    
    while not pQueue.empty():
        current = pQueue.get()
        # print("current", current)

        # Add the current node to the closed list
        # closed.append(current.position)

        #Using dictionary instead of a list, to make retrival easier
        closed_hash[current.position] = True

        # print("closed hash", closed_hash)

        # Check if we have reached the goal, return the path
        if current == end:
            print("Astar goal!")
            path = []
            while current != start:
                path.append(current.position)
                current = current.parent
            path.append(start.position) 
            # Return reversed path
            return path[::-1]

        for n in current.get_neigbours():
            #check if neighbor is in closed set
            if n.position in closed_hash:
                continue

            #calculate heuristics for the neighbor
            n.g = current.g + 1
            n.h = calc_manhattan(n.position, [grid_len-1,grid_len-1])
            n.f = n.g + n.h

            #check if node is in priority queue if yes does it have lower value?

            #add n to priority queue
            (x, y) = n.position
            if knowledge_grid[x][y] != 1:
                # print("add to queue", n)
                pQueue.insert(n,n.f)

    return None

def implement(matrix, knowledge, path):
  for itr in  range(1,len(path)):
    i = path[itr][0]
    j = path[itr][1]
    print("(i,j) -- ", i, j)
    if matrix[i][j] == 1:
      print("ended node", path[itr-1])  
      knowledge[i][j] = 1
      return path[itr-1]
    if i+1<len(matrix) and matrix[i+1][j]==1:
      knowledge[i+1][j] = 1
    if j+1<len(matrix) and matrix[i][j+1]==1:
      knowledge[i][j+1] = 1
    if i-1>0 and matrix[i-1][j]==1:
      knowledge[i-1][j] = 1
    if j-1>0 and matrix[i][j-1]==1:
      knowledge[i][j-1] = 1
  return path[len(path)-1]

def repeated(matrix, knowledge, start, end):
    flag = False
    #Update knowledge for the first time from the start position
    # i = j = 0
    # if i+1 < len(matrix) and matrix[i+1][j] == 1:
    #   knowledge[i+1][j] = 1
    # if j+1 < len(matrix[0]) and matrix[i][j+1] == 1:
    #   knowledge[i][j+1] = 1
    while True:
        print("################")
        print_grid(knowledge)
        path = astar(knowledge, start, end)
        print(path)

        if path:
            last = implement(matrix, knowledge, path)
            last_Node = Node(last)
            print("lastNode", last_Node)
            # if path[0] == last:
            #     print("error?")
            #     break
            if path[len(path)-1] == last:
                print("Agent goal!!")
                flag = True
                break
            start = last_Node

        else:
            print("no path planned it got stuck")
            break

    return 0        
    

######################################################
# Function calls after this

grid_len = 5
# matrix = create_grid(grid_len)
matrix = [[0,0,0,0,0],[0,1,1,1,1],[0,1,0,0,0],[0,1,0,0,0],[0,0,0,0,0]]
print_grid(matrix)

knowledge = [ [ 0 for i in range(grid_len) ] for j in range(grid_len) ]

print("")
print_grid(knowledge)
print("")

start = Node()
start.position = (0, 0)
goal = Node()
goal.position = (grid_len-1, grid_len-1)

print(repeated(matrix, knowledge, start, goal))

#Final output
print("knowledge")
print_grid(knowledge)
print("Final", astar(knowledge, start, goal))

######################################
# Things to do:
#     use hashmap instead of closed list - done
#     not sure but check this : add logic to check if the neighbor node is already in the priority queue and whether there is better heuristic for us to consider ?
#     check the infinite loop case - done
#     get path from all the traversed path by the Agent - done by using Astar again