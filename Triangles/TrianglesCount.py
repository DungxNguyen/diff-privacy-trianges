# Dung Nguyen

import networkx as nx

def total_triangles(G):
    return sum(list(nx.triangles(G).values())) // 3

G = nx.Graph()

G.add_nodes_from([1, 2, 3, 4])
G.add_edges_from([(1, 2), (1, 3), (2, 3)])

print(nx.triangles(G))

print(total_triangles(nx.complete_graph(4)))

print(total_triangles(G))

