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
import common
from concurrent.futures import ProcessPoolExecutor


def color_sample(net, p):
    sampled_net = nx.Graph()

    for node in net.nodes():
        net.nodes[node]['color'] = random.randint(1, math.ceil(1/p))

    for (u, v) in net.edges():
        if net.nodes[u]['color'] == net.nodes[v]['color']:
            sampled_net.add_edge(u, v)

    return sampled_net


def private_color_sample(net, epsilon, delta):
    p = min(1.0, delta)
    sampled_net = color_sample(net, p)
    return sampled_net


def private_color_triange_count(net, epsilon, delta):
    p = min(1.0, delta)
    sampled_net = color_sample(net, p)
    return common.triangle_count(sampled_net)[0] / (p**2)
