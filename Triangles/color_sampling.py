# Dung Nguyen
# Implement color sampling algorithm
import networkx as nx
import gurobipy as grb
import numpy as np
import math
import random
import shiva

network_path = "../data_graphs/ca-GrQc.txt"


def color_sample(net, p):
    sampled_net = nx.Graph()

    for node in net.nodes():
        net.nodes[node]['color'] = random.randint(1, math.ceil(1/p))

    for (u, v) in net.edges():
        if net.nodes[u] == net.nodes[v]:
            sampled_net.add_edge(u, v)

    return sampled_net


def shiva_color_sample(net, D, epsilon, p):
    return shiva.shiva_triange_count(color_sample(net, p), D, epsilon) / p ** 2


def main():
    net = nx.read_edgelist(network_path, create_using=nx.Graph(), nodetype=int)
    p = 0.5
    sampled_net = color_sample(net, p)

    print("Originial Nodes: ", net.number_of_nodes())
    print("Originial Edges: ", net.number_of_edges())
    print("Originial Triangles: ", shiva.total_triangles(net))
    print("Sampled Nodes: ", sampled_net.number_of_nodes())
    print("Sampled Edges: ", sampled_net.number_of_edges())
    print("Sampled Triangles: ", shiva.total_triangles(sampled_net))
    print("Estimated Triangles: ", shiva.total_triangles(sampled_net) / p ** 2)
    print("Estimated Shiva Triangles: ", shiva_color_sample(net, 50, 1, 0.5))
    

if __name__ == "__main__":
    main()
