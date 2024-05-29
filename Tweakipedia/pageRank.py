import numpy as np

# This code file contains the code that runs pageRank algorithm.

# class for the graph
class Graph:
    def __init__(self):
        self.nodes = []

    def contains(self, name):
        for node in self.nodes:
            if(node.name == name):
                return True
        return False

    # Return the node with the name, create and return new node if not found
    def find(self, name):
        if(not self.contains(name)):
            new_node = Node(name)
            self.nodes.append(new_node)
            return new_node
        else:
            return next(node for node in self.nodes if node.name == name)

    def add_edge(self, parent, child):
        parent_node = self.find(parent)
        child_node = self.find(child)

        parent_node.link_child(child_node)
        child_node.link_parent(parent_node)

    def display(self):
        for node in self.nodes:
            print(f'{node.name} links to {[child.name for child in node.children]}')

    def sort_nodes(self):
        self.nodes.sort(key=lambda node: int(node.name))

    def normalize_pagerank(self):
        pagerank_sum = sum(node.pagerank for node in self.nodes)

        for node in self.nodes:
            node.pagerank /= pagerank_sum

    def get_auth_hub_list(self):
        auth_list = np.asarray([node.auth for node in self.nodes], dtype='float32')
        hub_list = np.asarray([node.hub for node in self.nodes], dtype='float32')

        return np.round(auth_list, 3), np.round(hub_list, 3)

    def get_pagerank_list(self):
        pagerank_list = np.asarray([node.pagerank for node in self.nodes], dtype='float32')
        return np.round(pagerank_list, 3)

    def get_edges(self):
      edges = []
      for node in self.nodes:
          for child in node.children:
            edges.append([node.name, child.name])
      return np.array(edges)

# represents node int the graph
class Node:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.parents = []
        self.auth = 1.0
        self.hub = 1.0
        self.pagerank = 1.0

    def link_child(self, new_child):
        for child in self.children:
            if(child.name == new_child.name):
                return None
        self.children.append(new_child)

    def link_parent(self, new_parent):
        for parent in self.parents:
            if(parent.name == new_parent.name):
                return None
        self.parents.append(new_parent)

    def update_auth(self):
        self.auth = sum(node.hub for node in self.parents)

    def update_hub(self):
        self.hub = sum(node.auth for node in self.children)

    def update_pagerank(self, d, n):
        in_neighbors = self.parents
        pagerank_sum = sum((node.pagerank / len(node.children)) for node in in_neighbors)
        random_jumping = d / n
        self.pagerank = random_jumping + (1-d) * pagerank_sum




# def init_graph(fname):
#     with open(fname) as f:
#         lines = f.readlines()
#
#     graph = Graph()
#
#     for line in lines:
#         [parent, child] = line.strip().split(',')
#         graph.add_edge(parent, child)
#
#     graph.sort_nodes()
#
#     return graph



#one iteration of page rank
def PageRank_one_iter(graph, d):
    node_list = graph.nodes
    for node in node_list:
        node.update_pagerank(d, len(graph.nodes))
    graph.normalize_pagerank()
    # print(graph.get_pagerank_list())
    # print()

# the power iteration method
def PageRank(graph, d, iteration=100):
    for i in range(iteration):
        PageRank_one_iter(graph, d)


# if __name__ == '__main__':
#
#     iteration = 100
#     damping_factor = 0.15
#
#     graph = init_graph('./dataset/graph_4.txt')
#
#     PageRank(iteration, graph, damping_factor)
#     print(graph.get_pagerank_list())
#     for node in graph.nodes:
#       print(node.name, node.pa)


#builds the graph from adjacency matrix
def init_graph(data):
    graph = Graph()
    data_shape = data.shape
    for i in range(data_shape[0]):
      for j in range(data_shape[0]):
        if data[i][j] == 1:
          graph.add_edge(j, i)
    graph.sort_nodes()
    return graph

#main funtion to run page rank
def runPageRank(graph,headers, damping_factor = 0.15, iteration = 500):
    PageRank(graph, damping_factor, iteration)
    ranks = []

    for node in graph.nodes:
      ranks.append([headers[node.name], node.pagerank])

    return np.array(ranks)

# wrap the function runPageRank for easier use.
def pageRankMain(df_np, headers):
  graph = init_graph(df_np)
  ranks = runPageRank(graph, headers)
  header_rank_dict = dict(ranks)
  rank_vector = []
  for h in headers:
      if h in header_rank_dict:
          rank_vector.append(header_rank_dict[h])
      else:
        rank_vector.append(0)

  return rank_vector
  