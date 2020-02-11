# Dung Nguyen
# Implement color sampling algorithm
import networkx as nx
import gurobipy as grb
import numpy as np
import math
import random
import shiva
import csv
import sys
from concurrent.futures import ProcessPoolExecutor
import basic_edge
import color
import common
import time
import itertools

network_path = "../data_graphs/"

network_name = ["ca-GrQc", #5000
                "ca-HepTh", #10000
                "ca-HepPh", #12000
                "ca-AstroPh", #19000
                "ca-CondMat", #23133
                "email-Enron", #36000
                "loc-gowalla_edges", #200000
                ]

result_file = "blocki_node_private.csv"


def renumber_node_ids(net):
    count = 0
    node_map = {}
    for node in net.nodes():
        node_map[node] = count
        count += 1

    print("Renumber nodes:", count)

    new_net = nx.Graph()
    for (u, v) in net.edges():
        new_net.add_edge(node_map[u], node_map[v])
        
    return new_net


def g_c(c, x):
    if x == 0:
        x = 0.0000000001
    if x > (2 / (c + 1)):
        return c + 1
    if 0 < x and x <= (2 / (c + 1)):
        return 2 / x * math.exp(-1 + (c + 1) / 2 * x)
    #else should raise error


def S_beta(beta, d_hat, k, c=4):
    return math.exp(beta / c * d_hat) * g_c(c, beta / c) * (k ** 2) / 2


def blocki_node_triange_count(net, epsilon, k, reps):
    net = renumber_node_ids(net)

    num_nodes = nx.number_of_nodes(net)
    num_edges = nx.number_of_edges(net)

    # Linear Programming Model
    lpm = grb.Model()
    lpm.Params.LogFile = "gurobi.log"
    lpm.Params.LogToConsole = 0
    lpm.Params.Threads = 32

    print("Prepare to add vars")
    w = lpm.addVars(2 * num_edges, name="w")
    x = lpm.addVars(num_nodes, name="x")
    print("Finish to add vars")

    w_map = {}
    count = 0
    for (u, v) in net.edges():
        w_map[(u, v)] = w[count]
        count += 1
        w_map[(v, u)] = w[count]
        count += 1
        
    print("Prepare to add x constraints")
    lpm.addConstrs(x[i] >= 0 for i in range(num_nodes))
    print("Added x constraints")

    for (u, v) in net.edges():
        lpm.addConstr(w_map[(u, v)] >= 0)
        lpm.addConstr(w_map[(v, u)] >= 0)
        lpm.addConstr(w_map[(u, v)] >= 1 - x[u] - x[v])
        lpm.addConstr(w_map[(v, u)] >= 1 - x[u] - x[v])
        lpm.addConstr(w_map[(u, v)] <= 1)
        lpm.addConstr(w_map[(v, u)] <= 1)

    for i in range(num_nodes):
        lpm.addConstr(grb.quicksum(w_map[(i, j)]
                                   for j in nx.neighbors(net, i)) <= k)

    print("Add all constraints")

    lpm.setObjective(grb.quicksum(x[i] for i in range(num_nodes)),
                     grb.GRB.MINIMIZE)

    lpm.optimize()

    # return lpm.ObjVal
    x_star = {}
    for v in lpm.getVars():
        if "x" in v.varName:
            index = int(v.varName[2:-1])
            x_star[index] = v.x
        #if "w" in v.varName:
        #    if v.x < 1.0:
        #        print(v.x)

    trim_net = nx.Graph()

    for (u, v) in net.edges():
        if x_star[u] < 1/4 and x_star[v] < 1/4:
            trim_net.add_edge(u, v)

    count = common.triangle_count(trim_net)[0]
    print("Trim count:", count)

    result = {}
    for eps in epsilon:
        delta = eps
        if delta == 1.0:
            delta = 0.999 #to avoid division by 0
        result[eps] = count + np.random.laplace(0,
                                                S_beta(beta=-eps / 2 * math.log(delta),
                                                       d_hat=2 * num_edges / num_nodes,
                                                       k=k,
                                                       c=4) / eps,
                                                reps)
    return result


def main():
    csvfile = open(result_file, 'a')
    result_writer = csv.writer(csvfile, delimiter=',',
                       quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for net_name in network_name:
        print("Net:", net_name)
        net = nx.read_edgelist(network_path + net_name + ".txt",
                       create_using=nx.Graph(),
                       nodetype=int)
 
        true_triangle_count = common.triangle_count(net)[0]
 
        #print("True count:", true_triangle_count)
        epsilon = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0] 
        #print("Epsilon/Delta:", epsilon, delta)
        blocki_100_triangle = blocki_node_triange_count(net, epsilon, 100, reps=int(sys.argv[1]))
        blocki_1000_triangle = blocki_node_triange_count(net, epsilon, 1000, reps=int(sys.argv[1]))
        for eps in epsilon:
            for sample in np.nditer(blocki_100_triangle[eps]):
                result_writer.writerow([time.time(),
                                        "node_privacy",
                                        "blocki_node_100",
                                        net_name,
                                        true_triangle_count,
                                        sample,
                                        eps,
                                        eps])
 
            for sample in np.nditer(blocki_1000_triangle[eps]):
                result_writer.writerow([time.time(),
                                        "node_privacy",
                                        "blocki_node_1000",
                                        net_name,
                                        true_triangle_count,
                                        sample,
                                        eps,
                                        eps])
            csvfile.flush()


def main2():
    net = nx.Graph()

    net.add_edge(1, 2)

    for (u, v) in net.edges():
        print(u, v)

if __name__ == "__main__":
    main()
