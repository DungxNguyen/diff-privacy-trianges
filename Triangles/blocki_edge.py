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

def blocki_edge_trim(net, k):

    sampled_net = nx.create_empty_copy(net)

    for (u, v) in net.edges():
        if sampled_net.degree(u) < k and sampled_net.degree(v) < k:
            sampled_net.add_edge(u, v)

    return sampled_net


def private_edge_blocki_triangle_count(net, epsilon, k, reps):
    trim_net = blocki_edge_trim(net, k)
    triangle_count = common.triangle_count(trim_net)[0]
    # print(triangle_count)
    # return np.random.laplace(0, 9 * (k ** 2) / epsilon, reps) + triangle_count
    return np.random.laplace(0, 3/2 * (k ** 2) / epsilon, reps) + triangle_count


network_path = "../data_graphs/"

network_name = ["ca-GrQc", #5000
                "ca-HepTh", #10000
                "ca-HepPh", #12000
                "ca-AstroPh", #19000
                "ca-CondMat", #23133
                "email-Enron", #36000
                "loc-gowalla_edges", #200000
                ]

result_file = "blocki_edge_private.csv"


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
        for epsilon in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]:
            delta = epsilon
            #print("Epsilon/Delta:", epsilon, delta)
            blocki_100_triangle = private_edge_blocki_triangle_count(net,
                                                                     epsilon,
                                                                     100,
                                                                     int(sys.argv[1])
                                                                     )
            for sample in np.nditer(blocki_100_triangle):
                result_writer.writerow([time.time(),
                                        "edge_privacy",
                                        "blocki_edge_100",
                                        net_name,
                                        true_triangle_count,
                                        sample,
                                        epsilon,
                                        delta])
 
            blocki_1000_triangle = private_edge_blocki_triangle_count(net,
                                                                      epsilon,
                                                                      1000,
                                                                      int(sys.argv[1])
            )
            for sample in np.nditer(blocki_1000_triangle):
                result_writer.writerow([time.time(),
                                        "edge_privacy",
                                        "blocki_edge_1000",
                                        net_name,
                                        true_triangle_count,
                                        sample,
                                        epsilon,
                                        delta])
            csvfile.flush()

if __name__ == "__main__":
    main()
