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

result_file = "result_edge_count.csv"


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

        origin_edge_count = net.number_of_edges()

        for epsilon in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]:
            delta = epsilon
            result_writer.writerow([time.time(),
                                    "edge_privacy",
                                    "origin",
                                    net_name,
                                    origin_edge_count,
                                    origin_edge_count,
                                    epsilon,
                                    delta])

            for _ in range(int(sys.argv[1])):
                edge_sampled_net = basic_edge.private_basic_edge_sample(net,
                                                                        epsilon,
                                                                        delta)
                result_writer.writerow([time.time(),
                                        "edge_privacy",
                                        "basic_edge",
                                        net_name,
                                        edge_sampled_net.number_of_edges(),
                                        origin_edge_count,
                                        epsilon,
                                        delta])

                color_sampled_net = color.private_color_sample(net,
                                                               epsilon,
                                                               delta)

                result_writer.writerow([time.time(),
                                        "edge_privacy",
                                        "color",
                                        net_name,
                                        color_sampled_net.number_of_edges(),
                                        origin_edge_count,
                                        epsilon,
                                        delta])


if __name__ == "__main__":
    main()
