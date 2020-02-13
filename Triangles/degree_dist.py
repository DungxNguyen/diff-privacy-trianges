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
import collections


network_path = "../data_graphs/"

network_name = ["ca-GrQc", #5000
                "ca-HepTh", #10000
                "ca-HepPh", #12000
                "ca-AstroPh", #19000
                "ca-CondMat", #23133
                "email-Enron", #36000
                "loc-gowalla_edges", #200000
                ]

result_file = "result_degree_dist.csv"


LIMIT = 200


def compute_degree_distribution(net, limit=200):
    degree_sequence = sorted([d for n, d in net.degree()], reverse=True)  # degree sequence
    degreeCount = collections.Counter(degree_sequence)
    degreeCountList = zip(*degreeCount.items())

    dist = np.zeros(limit + 1)

    print(degreeCountList)
    for deg, count in degreeCountList:
        if deg <= limit:
            dist[deg] = count

    return dist


def main():
    csvfile = open(result_file, 'a')
    result_writer = csv.writer(csvfile, delimiter=',',
                       quotechar='|', quoting=csv.QUOTE_MINIMAL)

    #net_name = network_name[int(sys.argv[1])]
    for net_name in network_name:
        print("Net:", net_name)
        net = nx.read_edgelist(network_path + net_name + ".txt",
                           create_using=nx.Graph(),
                           nodetype=int)

        for epsilon in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]:
            delta = epsilon

            original_dist = compute_degree_distribution(net, limit=LIMIT)

            for i in range(LIMIT+1):
                result_writer.writerow([time.time(),
                                        "edge_privacy",
                                        "origin",
                                        net_name,
                                        i,
                                        original_dist[i],
                                        epsilon,
                                        delta])

            edge_sampled_dists = [] * int(sys.argv[1])
            color_sampled_dists = [] * int(sys.argv[1])
            for i in range(int(sys.argv[1])):
                edge_sampled_dists[i] = compute_degree_distribution(basic_edge.private_basic_edge_sample(net,
                                                                                                         epsilon,
                                                                                                         delta),
                                                                    limit=LIMIT)
                
                color_sampled_dists[i] = compute_degree_distribution(color.private_color_sample(net,
                                                                                                epsilon,
                                                                                                delta),
                                                                     limit=LIMIT)

            average_edge_dist = np.mean(np.array(edge_sampled_dists), axis=0) / min(1 - math.exp(-epsilon), delta, 1.0)
            average_color_dist = np.mean(np.array(color_sampled_dists), axis=0) / min(1.0, delta)

            for i in range(LIMIT + 1):
                result_writer.writerow([time.time(),
                                        "edge_privacy",
                                        "basic_edge",
                                        net_name,
                                        i,
                                        average_edge_dist[i],
                                        epsilon,
                                        delta])

                result_writer.writerow([time.time(),
                                        "edge_privacy",
                                        "color",
                                        net_name,
                                        i,
                                        average_color_dist[i],
                                        epsilon,
                                        delta])

                csvfile.flush()


if __name__ == "__main__":
    main()
