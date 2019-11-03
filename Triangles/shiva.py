# Dung Nguyen
# Implement Shiva algorithm
import networkx as nx
import gurobipy as grb
import numpy as np
import scipy.optimize as opt
import math
import timeit

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


def linear_program_solve(net, D, p=1, method="gurobi"):

    if method == "gurobi":
        return linear_program_solve_gurobi(net, D, p)

    return linear_program_solve_scipy(net, D, p)


def linear_program_solve_scipy(net, D, p=1):

    triangles = list_triangles(net)

    num_triangles = len(triangles)

    number_of_nodes = net.number_of_nodes()

    c = np.ones(num_triangles) * -1

    P = np.zeros((number_of_nodes, num_triangles))

    p = np.ones(number_of_nodes) * (D * (D-1) / 2)

    for i in range(number_of_nodes):
        for j in range(num_triangles):
            if i in triangles[j]:
                P[i][j] = 1

    start = timeit.default_timer()

    lp = opt.linprog(c, A_ub=P, b_ub=p, bounds=(0, 1))

    end = timeit.default_timer()
    duration = end - start

    print("LP Solver time: ", duration)

    return -lp.fun


def linear_program_solve_gurobi(net, D, p=1):
    triangles = list_triangles(net)

    # Linear Programming Model
    lpm = grb.Model()
    lpm.Params.LogFile = "gurobi.log"

    num_triangles = len(triangles)
    # print("Real count triangles: ", num_triangles)

    x = lpm.addVars(len(triangles), name="x_C")

    lpm.addConstrs(x[i] >= 0 for i in range(num_triangles))
    lpm.addConstrs(x[i] <= 1 for i in range(num_triangles))

    for node in net.nodes():
        lpm.addConstr(grb.quicksum(x[i]
                                   for i in range(num_triangles)
                                   if node in triangles[i]) <= p * D * (D * p - 1) / 2) # A node in a D-bounded graph can involve in at most 1/2D(D-1) triangles

    lpm.setObjective(grb.quicksum(x[i] for i in range(num_triangles)),
                     grb.GRB.MAXIMIZE)

    lpm.optimize()

    return lpm.ObjVal


def shiva_differentially_private_triange_count(net, D, epsilon, method="gurobi"):
    real_triangle_count = total_triangles(net)

    number_of_nodes = net.number_of_nodes()
    # print("Nodes: ", number_of_nodes)

    threshold = number_of_nodes ** 2 * math.log(number_of_nodes) / epsilon
    # print("Threshold: ", threshold)

    f1_hat = real_triangle_count + np.random.laplace(0, 6 * number_of_nodes ** 2 / epsilon)

    if f1_hat > 7 * threshold:
        return f1_hat

    lpm = linear_program_solve(net, D, method)
    print("LP Count: ", lpm)
    noise = np.random.laplace(0, 6 * D ** 2 / epsilon)
    f2_hat = lpm + noise

    print("Noise: ", noise)

    return f2_hat


def total_triangles(G):
    return sum(list(nx.triangles(G).values())) // 3


def main():
    net = nx.read_edgelist(network_path, create_using=nx.Graph(), nodetype=int)

    n_node = 5000
    edge_prob = 0.0125

    net = nx.fast_gnp_random_graph(n_node, edge_prob)
    # real count by networkx
    print("Real count triangles: ", total_triangles(net))

    d_bound = max(val for (node, val) in net.degree())
    # shiva algorithm with D = 50
    shiva_count = shiva_differentially_private_triange_count(net, d_bound, 1, "scipy")

    print("Shiva alg count: ", shiva_count)


if __name__ == "__main__":
    main()
