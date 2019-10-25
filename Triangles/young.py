# Dung Nguyen
# Implementation of young algorithm for counting triangles
import networkx as nx
import gurobipy as grb
import numpy as np
import math
import random
import shiva
import timeit



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
    if i not in nodes.keys():
        return sum_x
    for triangle in nodes[i]:
        sum_x += X[triangle]

    return sum_x


def normP(nodes, X, N, D):
    triangle_norm = np.sum(np.exp(X * N))

    node_norm = 0
    for node in nodes.keys():
        node_norm += np.exp(2 * N / (D * (D - 1)) * sum_triangles_of_node(node, nodes, X))

    return triangle_norm + node_norm


def partialP(j, nodes, triangles, X, N, D):
    triangle_sum = N * np.exp(N * X[j])

    node_sum = 0

    for node in triangles[j]:
        node_sum += (2 * N / (D * (D - 1))) * \
                np.exp((2 * N / (D * (D - 1))) * \
                       sum_triangles_of_node(node, nodes, X))

    return (triangle_sum + node_sum)


def young_triangle_count(net, c, D, epsilon):
    (count, triangles, nodes) = triangle_count(net)
    T = count
    N = (2 * math.log(T + net.number_of_nodes() + 1)) / epsilon
    alpha = epsilon / N
    X = np.zeros(T)

    print("N: ", N)

    start = timeit.default_timer()
    iter_count = 0
    node_table = {}
    while np.sum(X) < c:
        j_select = -1
        infeasible = True

        norm = normP(nodes, X, N, D)
        for j in range(T):
            ratio_j = partialP(j, nodes, triangles, X, N, D) / norm / (N / c)
            # print("partial", j, ": ", partialP(j, nodes, triangles, X, N, D))
            # print("ratio", j, ": ", ratio_j)
            if infeasible and ratio_j <= 1:
                infeasible = False
            if ratio_j <= 1 + epsilon:
                j_select = j
                if not infeasible:
                    break

        if infeasible:
            # print("X: ", X)
            return -1
        # Add alpha j to X
        iter_count += 1
        X[j_select] += alpha

        # This function call is used to update the node_table
        # Not need yet
        # partialP(j, nodes, triangles, X, N, D, node_table)
        # print("Iter: ", iter_count)
        # print("j index: ", j_select)
        # print("X: ", X)

        if (iter_count % 100 == 0):
            print("Iter ", iter_count, ": ", np.sum(X))

    # print("Triangles: ", triangles.items())
    # print("Nodes: ", nodes.items())

    end = timeit.default_timer()

    duration = end - start

    # print("X: ", X)
    print("Young Validate: ", validate(net, X, c, D, epsilon))
    print("Young time: ", duration)

    # TODO Fix the return value here
    return np.sum(X)


def validate(net, X, c, D, epsilon):
    (count, triangles, nodes) = triangle_count(net)
    if np.amax(X) > 1 + epsilon:
        return False
    for node in net.nodes():
        if sum_triangles_of_node(node, nodes, X) >= D * (D - 1) / 2 * (1 + epsilon):
            return False

    return True


def main():
    net = nx.read_edgelist(network_path, create_using=nx.Graph(), nodetype=int)

    n_node = 50
    edge_prob = 0.2

    net = nx.fast_gnp_random_graph(n_node, edge_prob)
    d_bound = max(val for (node, val) in net.degree())

    print("Nodes: ", net.number_of_nodes())
    print("D-Bound: ", d_bound)
    count, triangles, nodes = triangle_count(net)
    print("Triangles: ", count)

    #net = nx.Graph()
    #net.add_edges_from([(1, 2), (1, 3), (2, 3)])

    young_count = young_triangle_count(net, count, d_bound, 1)
    print("Real Count: ", count)
    print("Young count: ", young_count)


if __name__ == "__main__":
    main()