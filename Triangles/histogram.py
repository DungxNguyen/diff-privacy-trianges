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
import basic_node
import basic_edge
import color


network_path = "../data_graphs/"

network_name = ["ca-GrQc", #5000
                "ca-HepTh", #10000
                "ca-HepPh", #12000
                "ca-AstroPh", #19000
                "ca-CondMat", #23133
                "email-Enron", #36000
                "loc-gowalla_edges", #200000
                ]

result_file = "histogram.csv"


def private_basic_node_triangle_histogram(net, epsilon, delta):
    p = min(1 - math.exp(-epsilon), delta, 1.0)
    sampled_net = basic_node.basic_node_sample(net, p)
    sampled_histogram = triangle_histogram(sampled_net)
    # original_histogram = triangle_histogram(net)

    # num_print = min(10, len(sampled_histogram))
    # print(sampled_histogram[:num_print] / original_histogram[:num_print])
    return sampled_histogram


def private_basic_edge_triangle_histogram(net, epsilon, delta):
    p = min(1 - math.exp(-epsilon), delta, 1.0)
    sampled_net = basic_edge.basic_edge_sample(net, p)
    sampled_histogram = triangle_histogram(sampled_net)
    # original_histogram = triangle_histogram(net)

    # num_print = min(10, len(sampled_histogram))
    # print(sampled_histogram[:num_print] / original_histogram[:num_print])
    return sampled_histogram


def private_color_triangle_histogram(net, epsilon, delta):
    p = min(1.0, delta)
    sampled_net = color.color_sample(net, p)
    sampled_histogram = triangle_histogram(sampled_net)
    # original_histogram = triangle_histogram(net)

    # num_print = min(10, len(sampled_histogram))
    # print(sampled_histogram[:num_print] / original_histogram[:num_print])
    return sampled_histogram


def triangle_histogram(net, density=True):
    (count, triangles, nodes) = common.triangle_count(net)

    triangle_count_per_node = [len(nodes[node]) for node in nodes]

    # print(triangle_count_per_node)

    hist = np.histogram(triangle_count_per_node, bins=max(triangle_count_per_node), density=density)

    return hist[0]


def test_hist(net):
    (count, triangles, nodes) = common.triangle_count(net)

    hist = triangle_histogram(net, density=False)

    sum_hist = 0
    for i in range(len(hist)):
        sum_hist += (i + 1) * hist[i]

    if count != sum_hist / 3:
        print("Error hist. Count:", count, "Hist:", sum_hist / 3)
    else:
        print("Sum correct")


def main():
    csvfile = open(result_file, 'a')
    result_writer = csv.writer(csvfile, delimiter=',',
                       quotechar='|', quoting=csv.QUOTE_MINIMAL)

    # for net_name in network_name:
    #     net = nx.read_edgelist(network_path + net_name + ".txt",
    #                        create_using=nx.Graph(),
    #                        nodetype=int)
    #     test_hist(net)
    #     true_histogram = triangle_histogram(net, density=True)
    #     for i in range(100):
    #         result_writer.writerow([time.time(),
    #                                 "node_privacy",
    #                                 "true_hist",
    #                                 net_name,
    #                                 0.5,
    #                                 0.5,
    #                                 i+1,
    #                                 true_histogram[i]
    #         ])

    for i in range(int(sys.argv[1])):
        print("Repeat:", i)
        for net_name in network_name:
            print("Net:", net_name)
            net = nx.read_edgelist(network_path + net_name + ".txt",
                           create_using=nx.Graph(),
                           nodetype=int)

            for epsilon in [0.1]:
                delta = epsilon
                basic_node_histogram = private_basic_node_triangle_histogram(net,
                                                                            epsilon,
                                                                            delta)
                for i in range(min(100, len(basic_node_histogram))):
                    result_writer.writerow([time.time(),
                                            "node_privacy",
                                            "basic_node",
                                            net_name,
                                            epsilon,
                                            delta,
                                            i+1,
                                            basic_node_histogram[i]
                    ])

                basic_edge_histogram = private_basic_edge_triangle_histogram(net,
                                                                            epsilon,
                                                                            delta)
                for i in range(min(100, len(basic_edge_histogram))):
                    result_writer.writerow([time.time(),
                                            "node_privacy",
                                            "basic_edge",
                                            net_name,
                                            epsilon,
                                            delta,
                                            i+1,
                                            basic_edge_histogram[i]
                    ])

                color_histogram = private_color_triangle_histogram(net,
                                                                            epsilon,
                                                                            delta)
                for i in range(min(100, len(color_histogram))):
                    result_writer.writerow([time.time(),
                                            "node_privacy",
                                            "color",
                                            net_name,
                                            epsilon,
                                            delta,
                                            i+1,
                                            color_histogram[i]
                    ])
                csvfile.flush()


if __name__ == "__main__":
    main()
