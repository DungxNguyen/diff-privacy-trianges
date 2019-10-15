# Dung Nguyen
# Implement Shiva algorithm
import networkx as nx
import gurobipy as grb

network_path = "../data_graphs/ca-GrQc.txt"

net = nx.read_edgelist(network_path, create_using=nx.Graph(), nodetype=int)


def list_triangles(network):
    list_of_triangles = []

    for i in net.nodes():
        for j in net.neighbors(i):
            for k in net.neighbors(j):
                if i < j and j < k and \
                   net.has_edge(i, k):
                    list_of_triangles.append((i, j, k))

    return list_of_triangles


triangles = list_triangles(net)

# Linear Programming Model
lpm = grb.Model()

D = 6000

num_triangles = len(triangles)
print("Real count triangles: ", num_triangles)

x = lpm.addVars(len(triangles), name="x_C")

lpm.addConstrs(x[i] >= 0 for i in range(num_triangles))
lpm.addConstrs(x[i] <= 1 for i in range(num_triangles))

for node in net.nodes():
    lpm.addConstr(grb.quicksum(x[i]
                  for i in range(num_triangles) if node in triangles[i]) <= D)


lpm.setObjective(grb.quicksum(x[i] for i in range(num_triangles)),
                 grb.GRB.MAXIMIZE)

lpm.optimize()
