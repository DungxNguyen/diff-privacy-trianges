# Dung Nguyen
# Implement Shiva algorithm
import networkx as nx
import gurobipy as grb
import numpy as np
import scipy.optimize as opt
import math
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


def triangle_count_ding(net):
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
                        nodes[i] = set()
                    if j not in nodes:
                        nodes[j] = set()
                    if k not in nodes:
                        nodes[k] = set()
                    nodes[i].add((j, k))
                    nodes[j].add((i, k))
                    nodes[k].add((i, j))
                    count += 1

    return (count, triangles, nodes)


def list_triangles(net):
    list_of_triangles = []

    for i in net.nodes():
        for j in net.neighbors(i):
            for k in net.neighbors(j):
                if i < j and j < k and \
                   net.has_edge(i, k):
                    list_of_triangles.append((i, j, k))

    return list_of_triangles
