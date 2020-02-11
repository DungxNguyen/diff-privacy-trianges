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


network_path = "../data_graphs/"

network_name = ["ca-GrQc", #5000
                "ca-HepTh", #10000
                "ca-HepPh", #12000
                "ca-AstroPh", #19000
                "ca-CondMat", #23133
                "email-Enron", #36000
                "loc-gowalla_edges", #200000
                ]

result_file = "basic_node_private.csv"


def basic_node_sample(net, p):
    if (p <= 0 and p > 1):
        return net  # Should raise exception

    sampled_nodes = []

    for v in net.nodes():
        if random.random() <= p:
            sampled_nodes.append(v)

    sampled_net = nx.subgraph(net, sampled_nodes)

    return sampled_net


def private_basic_node_sample(net, epsilon, delta):
    p = min(1 - math.exp(-epsilon), delta, 1.0)
    sampled_net = basic_node_sample(net, p)
    return sampled_net


def private_basic_node_triangle_count(net, epsilon, delta):
    p = min(1 - math.exp(-epsilon), delta, 1.0)
    sampled_net = basic_node_sample(net, p)
    return common.triangle_count(sampled_net)[0] / (p ** 3)


def main():
    csvfile = open(result_file, 'a')
    result_writer = csv.writer(csvfile, delimiter=',',
                       quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for i in range(int(sys.argv[1])):
        print(i)
        for net_name in network_name:
            print("Net:", net_name)
            net = nx.read_edgelist(network_path + net_name + ".txt",
                           create_using=nx.Graph(),
                           nodetype=int)

            true_triangle_count = common.triangle_count(net)[0]

            #print("True count:", true_triangle_count)
            for epsilon in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]:
                delta = epsilon
                #print("Epsilon/Delta:", epsilon, delta)
                basic_node_triangle = private_basic_node_triangle_count(net,
                                                                        epsilon,
                                                                        delta
                )
                result_writer.writerow([time.time(),
                                        "node_privacy",
                                        "basic_node",
                                        net_name,
                                        true_triangle_count,
                                        basic_node_triangle,
                                        epsilon,
                                        delta])

                csvfile.flush()


if __name__ == "__main__":
    main()
