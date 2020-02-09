# Dung Nguyen
# Implement Shiva algorithm
import networkx as nx
import gurobipy as grb
import numpy as np
import scipy.optimize as opt
import math
import timeit
import common
import random

network_path = "../data_graphs/ca-GrQc.txt"


def basic_edge_sample(net, p):
    if (p <= 0 and p > 1):
        return net  # Should raise exception

    sampled_net = nx.Graph()

    for (u, v) in net.edges():
        if random.random() <= p:
            sampled_net.add_edge(u, v)

    return sampled_net


def private_basic_edge_triange_count(net, epsilon, delta):
    p = min(1 - math.exp(-epsilon), delta, 1.0)
    sampled_net = basic_edge_sample(net, p)
    return common.triangle_count(sampled_net)[0] / (p**3)
