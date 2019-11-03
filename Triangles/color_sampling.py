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

network_path = ["../data_graphs/ca-GrQc.txt", #5000
                "../data_graphs/ca-HepTh.txt", #10000
                "../data_graphs/ca-HepPh.txt", #12000
                "../data_graphs/ca-AstroPh.txt", #19000
                "../data_graphs/ca-CondMat.txt", #23133
                "../data_graphs/email-Enron.txt", #36000
                "../data_graphs/loc-gowalla_edges.txt", #200000
                ]


def color_sample(net, p):
    sampled_net = nx.Graph()

    for node in net.nodes():
        net.nodes[node]['color'] = random.randint(1, math.ceil(1/p))

    for (u, v) in net.edges():
        if net.nodes[u]['color'] == net.nodes[v]['color']:
            sampled_net.add_edge(u, v)

    return sampled_net


def shiva_color_sample(net, D, p):
    return shiva.linear_program_solve(color_sample(net, p), D, p) / p ** 2


def run_experiments(net):
    d_bound = max(val for (node, val) in net.degree())
    for d in range(5):
        D = d_bound / (2 ** d)
        original_lp = shiva.linear_program_solve(net, D)

        for k in range(5):
            p = 1 / (2 ** (k + 1))
            try:
                experiment(net, D, p, original_lp)
            except:
                with open(network_path[int(sys.argv[1])] + ".csv", 'a') as csvfile:
                    logwriter = csv.writer(csvfile, delimiter=',',
                                           quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    logwriter.writerow([D, p, original_lp, -1, -1])


def experiment(net, D, p, original_lp, repeat=None):
    with open(network_path[int(sys.argv[1])] + ".csv", 'a') as csvfile:
        if repeat is None:
            repeat = int(round(2 * math.log2(net.number_of_nodes())))

        # original_lp = shiva.linear_program_solve(net, D)

        sample_lp = 0
        for i in range(repeat):
            sample_lp += shiva_color_sample(net, D, p)

        sample_lp /= repeat

        logwriter = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        logwriter.writerow([D, p, original_lp, sample_lp, original_lp / sample_lp])
        print(D,  p, original_lp, sample_lp, original_lp / sample_lp)

    return (sample_lp, original_lp)


def main():
    net = nx.read_edgelist(network_path[int(sys.argv[1])],
                           create_using=nx.Graph(),
                           nodetype=int)
    # n_node = 10000
    # edge_prob = 0.0120

    # net = nx.fast_gnp_random_graph(n_node, edge_prob)
    # p = 0.125
    # sampled_net = color_sample(net, p)
    # d_bound = max(val for (node, val) in net.degree())

    # print("Originial Nodes: ", net.number_of_nodes())
    # print("Originial Edges: ", net.number_of_edges())
    # print("Originial Triangles: ", shiva.total_triangles(net))
    # print("Sampled Nodes: ", sampled_net.number_of_nodes())
    # print("Sampled Edges: ", sampled_net.number_of_edges())
    # print("Sampled Triangles: ", shiva.total_triangles(sampled_net))
    # print("Estimated Triangles: ", shiva.total_triangles(sampled_net) / p ** 2)
    # print("Estimated Shiva LP Triangles: ", shiva_color_sample(net, d_bound, p))
    run_experiments(net)


if __name__ == "__main__":
    main()
