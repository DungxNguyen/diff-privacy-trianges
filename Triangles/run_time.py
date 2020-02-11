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
import timeit


network_path = "../data_graphs/"

network_name = ["ca-GrQc", #5000
                "ca-HepTh", #10000
                "ca-HepPh", #12000
                "ca-AstroPh", #19000
                "ca-CondMat", #23133
                "email-Enron", #36000
                "loc-gowalla_edges", #200000
                ]

result_file = "runtime.csv"


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

    for i in range(int(sys.argv[1])):
        print("Repeat:", i)
        for net_name in network_name:
            print("Net:", net_name)
            net = nx.read_edgelist(network_path + net_name + ".txt",
                                   create_using=nx.Graph(),
                                   nodetype=int)
            net.remove_edges_from(nx.selfloop_edges(net))

            print("Original")
            start = timeit.default_timer()
            common.triangle_count(net)
            end = timeit.default_timer()
            true_runtime = end - start

            for epsilon in [1, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001]:
                result_writer.writerow([time.time(),
                                        "node_privacy",
                                        "original",
                                        "runtime",
                                        net_name,
                                        epsilon,
                                        epsilon,
                                        i,  # reserve for index
                                        true_runtime
                   ])

            print("Sampling")
            for epsilon in [1, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001]:
                delta = epsilon

                start = timeit.default_timer()
                basic_node.private_basic_node_triangle_count(net, epsilon, delta)
                end = timeit.default_timer()
                runtime = end - start

                result_writer.writerow([time.time(),
                                        "node_privacy",
                                        "basic_node",
                                        "runtime",
                                        net_name,
                                        epsilon,
                                        delta,
                                        i, #reserve for index
                                        runtime 
                ])

                start = timeit.default_timer()
                basic_edge.private_basic_edge_triange_count(net, epsilon, delta)
                end = timeit.default_timer()
                runtime = end - start

                result_writer.writerow([time.time(),
                                        "edge_privacy",
                                        "basic_edge",
                                        "runtime",
                                        net_name,
                                        epsilon,
                                        delta,
                                        i, #reserve for index
                                        runtime 
                ])

                start = timeit.default_timer()
                color.private_color_triange_count(net, epsilon, delta)
                end = timeit.default_timer()
                runtime = end - start

                result_writer.writerow([time.time(),
                                        "edge_privacy",
                                        "color",
                                        "runtime",
                                        net_name,
                                        epsilon,
                                        delta,
                                        i, #reserve for index
                                        runtime 
                ])

                csvfile.flush()

            print("blocki")
            start = timeit.default_timer()
            blocki_edge.private_edge_blocki_triangle_count(net, epsilon, 100, 1)
            end = timeit.default_timer()
            blocki_edge_100_runtime = end - start

            print("blocki node")
            start = timeit.default_timer()
            blocki_node.blocki_node_triangle_count(net, epsilon, 100, 1)
            end = timeit.default_timer()
            blocki_node_100_runtime = end - start

            print("shiva")
            start = timeit.default_timer()
            shiva.shiva_differentially_private_triange_count(net, 100, epsilon, method="gurobi", reps=1)
            end = timeit.default_timer()
            shiva_100_runtime = end - start
            # start = timeit.default_timer()
            # ding.blocki_node_triangle_count(net, epsilon, 100, 1)
            # end = timeit.default_timer()
            # ding_26_runtime = end - start

            for epsilon in [1, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001]:
                result_writer.writerow([time.time(),
                                        "edge_privacy",
                                        "blocki_edge_100",
                                        "runtime",
                                        net_name,
                                        epsilon,
                                        epsilon,
                                        i, #reserve for index
                                        blocki_edge_100_runtime 
                   ])

                result_writer.writerow([time.time(),
                                        "node_privacy",
                                        "blocki_node_100",
                                        "runtime",
                                        net_name,
                                        epsilon,
                                        epsilon,
                                        i, #reserve for index
                                        blocki_node_100_runtime

                   ])
                result_writer.writerow([time.time(),
                                        "node_privacy",
                                        "shiva_100",
                                        "runtime",
                                        net_name,
                                        epsilon,
                                        epsilon,
                                        i, #reserve for index
                                        shiva_100_runtime
                   ])

                csvfile.flush()


if __name__ == "__main__":
    main()
