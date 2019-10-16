# Dung Nguyen
# Implement Shiva algorithm
import networkx as nx
import gurobipy as grb

network_path = "../data_graphs/ca-GrQc.txt"


def list_triangles(net):
    list_of_triangles = []

    for i in net.nodes():
        for j in net.neighbors(i):
            for k in net.neighbors(j):
                if i < j and j < k and \
                   net.has_edge(i, k):
                    list_of_triangles.append((i, j, k))

    return list_of_triangles


def shiva_triange_count(net, D):

    triangles = list_triangles(net)

    # Linear Programming Model
    lpm = grb.Model()

    num_triangles = len(triangles)
    # print("Real count triangles: ", num_triangles)

    x = lpm.addVars(len(triangles), name="x_C")

    lpm.addConstrs(x[i] >= 0 for i in range(num_triangles))
    lpm.addConstrs(x[i] <= 1 for i in range(num_triangles))

    for node in net.nodes():
        lpm.addConstr(grb.quicksum(x[i]
                                   for i in range(num_triangles)
                                   if node in triangles[i]) <= D * (D - 1) / 2) # A node in a D-bounded graph can involve in at most 1/2D(D-1) triangles

    lpm.setObjective(grb.quicksum(x[i] for i in range(num_triangles)),
                     grb.GRB.MAXIMIZE)

    return lpm


def total_triangles(G):
    return sum(list(nx.triangles(G).values())) // 3


def main():
    net = nx.read_edgelist(network_path, create_using=nx.Graph(), nodetype=int)

    # shiva algorithm with D = 50
    lpm = shiva_triange_count(net, 50)

    lpm.optimize()

    # real count by networkx
    print("Real count triangles: ", total_triangles(net))

    print("Shiva alg count: ", lpm.ObjVal)


if __name__ == "__main__":
    main()
