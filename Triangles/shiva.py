# Dung Nguyen
# Implement Shiva algorithm
import networkx as nx
import gurobipy as grb
import numpy as np
import math

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

def linear_program_solve(net, D):
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

    lpm.optimize()

    return lpm.ObjVal


def shiva_triange_count(net, D, epsilon):
    real_triangle_count = total_triangles(net)

    number_of_nodes = net.number_of_nodes()
    # print("Nodes: ", number_of_nodes)

    threshold = number_of_nodes ** 2 * math.log(number_of_nodes) / epsilon
    # print("Threshold: ", threshold)

    f1_hat = real_triangle_count + np.random.laplace(6 * number_of_nodes ** 2 / epsilon)

    if f1_hat > 7 * threshold:
        return f1_hat

    f2_hat = linear_program_solve(net, D) + np.random.laplace(6 * D ** 2 / epsilon)

    return f2_hat


def total_triangles(G):
    return sum(list(nx.triangles(G).values())) // 3


def main():
    net = nx.read_edgelist(network_path, create_using=nx.Graph(), nodetype=int)

    # shiva algorithm with D = 50
    shiva_count = shiva_triange_count(net, 50, 1)

    # real count by networkx
    print("Real count triangles: ", total_triangles(net))

    print("Shiva alg count: ", shiva_count)


if __name__ == "__main__":
    main()
