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

result_file = "k_core_metrics.csv"


def main():
    csvfile = open(result_file, 'a')
    result_writer = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for net_name in network_name:
        net = nx.read_edgelist(network_path + net_name + ".txt",
                               create_using=nx.Graph(),
                               nodetype=int)
        net.remove_edges_from(nx.selfloop_edges(net))
        for k in [16, 8, 4]:
            true_k_core = nx_core.k_core(net, k).number_of_nodes()
            result_writer.writerow([time.time(),
                                    "node_privacy",
                                    "true",
                                    "k_core",
                                    net_name,
                                    0.5,
                                    0.5,
                                    k,  # reserve for index
                                    true_k_core
            ])

    for i in range(int(sys.argv[1])):
        print("Repeat:", i)
        for net_name in network_name:
            print("Net:", net_name)
            net = nx.read_edgelist(network_path + net_name + ".txt",
                                   create_using=nx.Graph(),
                                   nodetype=int)

            net.remove_edges_from(nx.selfloop_edges(net))
            for k in [16, 8, 4]:
                for epsilon in [1, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001]:
                    delta = epsilon
                    basic_node_k_core = nx_core.k_core(basic_node.private_basic_node_sample(net,
                                                                                              epsilon,
                                                                                              delta), k).number_of_nodes()
                    result_writer.writerow([time.time(),
                                            "node_privacy",
                                            "basic_node",
                                            "k_core",
                                            net_name,
                                            epsilon,
                                            delta,
                                            k, #reserve for index
                                            basic_node_k_core
                    ])

                    basic_edge_k_core = nx_core.k_core(basic_edge.private_basic_edge_sample(net,
                                                                                                    epsilon,
                                                                                                    delta), k).number_of_nodes()
                    result_writer.writerow([time.time(),
                                            "edge_privacy",
                                            "basic_edge",
                                            "k_core",
                                            net_name,
                                            epsilon,
                                            delta,
                                            k,
                                            basic_edge_k_core
                    ])

                    color_k_core = nx_core.k_core(color.private_color_sample(net,
                                                                                     epsilon,
                                                                                     delta), k).number_of_nodes()
                    result_writer.writerow([time.time(),
                                            "edge_privacy",
                                            "color",
                                            "k_core",
                                            net_name,
                                            epsilon,
                                            delta,
                                            k,
                                            color_k_core
                    ])
                    csvfile.flush()


if __name__ == "__main__":
    main()
