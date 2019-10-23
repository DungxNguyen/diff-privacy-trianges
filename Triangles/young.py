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
                    triangles[count] = (i, j, k)
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

def young_triangle_count(net, D, epsilon):
    (count, triangles, nodes) = triangle_count(net)

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
