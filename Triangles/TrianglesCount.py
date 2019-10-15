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


network_path = "../data_graphs/ca-GrQc.txt"

net = nx.read_edgelist(network_path, create_using=nx.Graph(), nodetype=int)

# 5242
print("Nodes: ", net.order())

# 14496
print("Edges: ", net.size())

# 48260
print("Triangles: ", total_triangles(net))


def list_triangles(network):
    list_of_triangles = []

    for i in net.nodes():
        for j in net.neighbors(i):
            for k in net.neighbors(j):
                if i < j and j < k and \
                   net.has_edge(i, k):
                    list_of_triangles.append([i, j, k])

    return list_of_triangles


print("Recount triangles: ", len(list_triangles(net)))

print("10 triangles: ", list_triangles(net)[0:10])
