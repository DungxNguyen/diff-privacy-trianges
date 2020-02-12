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
import basic_node
import blocki_edge
import blocki_node
import ding
import color
import common
import time
import networkx.algorithms.distance_measures as nx_distance
import networkx.algorithms.core as nx_core


network_path = "../data_graphs/"

network_name = ["ca-GrQc", #5000
                "ca-HepTh", #10000
                "ca-HepPh", #12000
                "ca-AstroPh", #19000
                "ca-CondMat", #23133
                "email-Enron", #36000
                "loc-gowalla_edges", #200000
                ]

result_file = "k_core_scale.csv"


def jaccard(G, H):
    G_nodes = list(G.nodes())
    H_nodes = list(H.nodes())

    intersection = len(set(G_nodes) & set(H_nodes))

    return intersection / (len(G_nodes) + len(H_nodes) - intersection)


def main():
    csvfile = open(result_file, 'a')
    result_writer = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)

    true_k_core = {}
    for net_name in network_name:
        net = nx.read_edgelist(network_path + net_name + ".txt",
                               create_using=nx.Graph(),
                               nodetype=int)
        net.remove_edges_from(nx.selfloop_edges(net))
        for k in [512, 256, 128, 64, 32, 16, 8, 4]:
            true_k_core[(net_name, k)] = nx_core.k_core(net, k)
            # result_writer.writerow([time.time(),
            #                         "node_privacy",
            #                         "true",
            #                         "k_core",
            #                         net_name,
            #                         0.5,
            #                         0.5,
            #                         k,  # reserve for index
            #                         true_k_core
            # ])

    for i in range(int(sys.argv[1])):
        print("Repeat:", i)
        for net_name in network_name:
            print("Net:", net_name)
            net = nx.read_edgelist(network_path + net_name + ".txt",
                                   create_using=nx.Graph(),
                                   nodetype=int)

            net.remove_edges_from(nx.selfloop_edges(net))
            for k in [512, 256, 128, 64, 32, 16, 8, 4]:
                for epsilon in [0.5, 0.1, 0.05]:
                    delta = epsilon
                    basic_node_k_core = nx_core.k_core(basic_node.private_basic_node_sample(net,
                                                                                              epsilon,
                                                                                              delta),
                                                       k * min(1 - math.exp(-epsilon), delta, 1.0) ** 2)
                    result_writer.writerow([time.time(),
                                            "node_privacy",
                                            "basic_node",
                                            "k_core",
                                            net_name,
                                            epsilon,
                                            delta,
                                            k, #reserve for index
                                            jaccard(true_k_core[(net_name, k)], basic_node_k_core)
                    ])

                    basic_edge_k_core = nx_core.k_core(basic_edge.private_basic_edge_sample(net,
                                                                                                    epsilon,
                                                                                                    delta),
                                                       k * min(1 - math.exp(-epsilon), delta, 1.0))
                    result_writer.writerow([time.time(),
                                            "edge_privacy",
                                            "basic_edge",
                                            "k_core",
                                            net_name,
                                            epsilon,
                                            delta,
                                            k,
                                            jaccard(true_k_core[(net_name, k)], basic_edge_k_core)
                    ])

                    color_k_core = nx_core.k_core(color.private_color_sample(net,
                                                                                     epsilon,
                                                                                     delta),
                                                  k * min(1.0, delta))
                    result_writer.writerow([time.time(),
                                            "edge_privacy",
                                            "color",
                                            "k_core",
                                            net_name,
                                            epsilon,
                                            delta,
                                            k,
                                            jaccard(true_k_core[(net_name, k)], color_k_core)
                    ])

                    csvfile.flush()

                blocki_edge_100_k_core = nx_core.k_core(blocki_edge.blocki_edge_trim(net,
                                                                                 100), k)
                for epsilon in [0.5, 0.1, 0.05]:
                    result_writer.writerow([time.time(),
                                            "edge_privacy",
                                            "blocki_edge_100",
                                            "k_core",
                                            net_name,
                                            epsilon,
                                            epsilon,    
                                            k,
                                            jaccard(true_k_core[(net_name, k)], blocki_edge_100_k_core)
                    ])

                blocki_edge_1000_k_core = nx_core.k_core(blocki_edge.blocki_edge_trim(net,
                                                                                 1000), k)
                for epsilon in [0.5, 0.1, 0.05]:
                    result_writer.writerow([time.time(),
                                            "edge_privacy",
                                            "blocki_edge_1000",
                                            "k_core",
                                            net_name,
                                            epsilon,
                                            epsilon,    
                                            k,
                                            jaccard(true_k_core[(net_name, k)], blocki_edge_1000_k_core)
                    ])

                ding_26_k_core = nx_core.k_core(ding.ding_trim(net,
                                                               100), k)
                for epsilon in [0.5, 0.1, 0.05]:
                    result_writer.writerow([time.time(),
                                            "edge_privacy",
                                            "ding_100",
                                            "k_core",
                                            net_name,
                                            epsilon,
                                            epsilon,    
                                            k,
                                            jaccard(true_k_core[(net_name, k)], ding_26_k_core)
                    ])

                csvfile.flush()


if __name__ == "__main__":
    main()
