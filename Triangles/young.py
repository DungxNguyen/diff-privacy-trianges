# Dung Nguyen
# Implementation of young algorithm for counting triangles
import networkx as nx
import gurobipy as grb
import numpy as np
import math
import random
import shiva

network_path = "../data_graphs/ca-GrQc.txt"

def triangle_count(net):
    triangles = {}
    nodes = {}
    count = 0

    for i in net.nodes():
        for j in net.neighbors(i):
            for k in net.neighbors(j):
                if i < j and j < k and \
                   net.has_edge(i, k):
                    triangles[count] = [i, j, k]
                    if i not in nodes:
                        nodes[i] = []
                    if j not in nodes:
                        nodes[j] = []
                    if k not in nodes:
                        nodes[k] = []
                    nodes[i].append(count)
                    nodes[j].append(count)
                    nodes[k].append(count)
                    count += 1

    return (count, triangles, nodes)


def sum_triangles_of_node(i, nodes, X):
    sum_x = 0
    for triangle in nodes[i]:
        sum_x += X[triangle]

    return sum_x


def normP(nodes, X, N):
    triangle_norm = np.sum(np.exp(X * N))

    node_norm = 0
    for node in nodes.keys():
        node_norm += np.exp(2 * N / (D * (D - 1)) * sum_triangles_of_node(node, nodes, X))

    return triangle_norm + node_norm

def partialP(j, nodes, triangles, X, N, D):
    triangle_sum = N * np.exp(N * X[j])

    node_sum = 0

    for node in triangles[j]:
        node_sum += (2 * N / (D * (D -1 ))) * \
            np.exp((2 * N / (D * (D -1 ))) * \
                   sum_triangles_of_node(node, nodes, X))

    return triangle_sum + node_sum


def young_triangle_count(net, c, D, epsilon):
    (count, triangles, nodes) = triangle_count(net)
    T = count
    N = 2 * math.log(T + net.number_of_nodes() + 1)
    alpha = epsilon / N
    X = np.zeros(T)

    while np.amin( N / c * X) < N:
        for j in range(T):
            ratio_j = partialP(j, nodes, triangles, X, N, D) / (N / c)
            if ratio_j < 1 + epsilon:
                break

        # Add alpha j to X
        X[j] += alpha

    print("Real Count: ", count)
    # print("Triangles: ", triangles.items())
    # print("Nodes: ", nodes.items())
    
    return 0
    

def main():
    net = nx.read_edgelist(network_path, create_using=nx.Graph(), nodetype=int)

    young_count = young_triangle_count(net, 50, 1):

    print("Young count: ", young_count)
    

if __name__ == "__main__":
    main()
