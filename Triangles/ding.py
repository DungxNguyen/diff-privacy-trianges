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
import basic_node_histogram


network_path = "../data_graphs/"

network_name = ["ca-GrQc", #5000
                "ca-HepTh", #10000
                "ca-HepPh", #12000
                "ca-AstroPh", #19000
                "ca-CondMat", #23133
                "email-Enron", #36000
                "loc-gowalla_edges", #200000
                ]

result_file = "ding_histogram.csv"


def ding_trim(net, lbda):
    # print(net.has_edge(0, 307))
    sampled_net = net.copy()

    (count, triangle, node_map) = common.triangle_count_ding(net)


    node_count = 0
    for node in sampled_net:
        if node_count % 100 == 0:
            print(node_count)
        node_count += 1
        if (node not in node_map) or (len(node_map[node]) <= lbda):
            continue
        neighbors = [n for n in sampled_net.neighbors(node)]
        neighbors_by_degree = sorted(neighbors, key=lambda n: sampled_net.degree(n), reverse=True)
        # print(neighbors_by_degree)
        for n in neighbors_by_degree:
            # print("n:", n)
            if len(node_map[node]) <= lbda:
                break
            for (u, v) in node_map[node].copy():
                # print("uv:", u, v)
                if n in (u, v):
                    node_map[node].discard((u, v))
                    node_map[node].discard((v, u))
                    node_map[u].discard((node, v))
                    node_map[u].discard((v, node))
                    node_map[v].discard((node, u))
                    node_map[v].discard((u, node))
                    if sampled_net.has_edge(node, n):
                        sampled_net.remove_edge(node, n)

    return sampled_net


def private_ding_triangle_hist(net, lbda, epsilon):
    sampled_net = ding_trim(net, lbda)

    hist = basic_node_histogram.triangle_histogram(sampled_net)

    noise = np.random.laplace(0, (4 * lbda + 1) / epsilon, len(hist))

    noisy_hist = hist + noise

    noisy_hist = noisy_hist / sum(noisy_hist)

    return noisy_hist 


def triangle_count_node(net, node):
    count = 0
    for j in net.neighbors(node):
        for k in net.neighbors(node):
            if j < k and net.has_edge(j, k):
                count += 1
    return count
    

def main():
    csvfile = open(result_file, 'a')
    result_writer = csv.writer(csvfile, delimiter=',',
                       quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for i in range(int(sys.argv[1])):
        print("Repeat", i)
        for net_name in network_name[-1:]:
            print("Net:", net_name)
            net = nx.read_edgelist(network_path + net_name + ".txt",
                           create_using=nx.Graph(),
                           nodetype=int)

            for epsilon in [0.5, 1.0]:
                delta = epsilon
                #print("Epsilon/Delta:", epsilon, delta)

                ding_histogram = private_ding_triangle_hist(net,
                                                            26,
                                                            epsilon,
                )
                for i in range(min(100, len(ding_histogram))):
                    result_writer.writerow([time.time(),
                                            "node_privacy",
                                            "ding",
                                            net_name,
                                            epsilon,
                                            delta,
                                            i+1,
                                            ding_histogram[i]
                    ])
                csvfile.flush()


if __name__ == "__main__":
    main()
