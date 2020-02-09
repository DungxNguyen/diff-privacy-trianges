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


def shiva_color_sample(net, D, p, c):
    print("****************************************", D, p)

    sampled_net = color_sample(net, p)
    return (shiva.linear_program_solve(sampled_net, D, p, c) / p ** 2,
            shiva.total_triangles(sampled_net))


# TODO: Fix run experiment
def run_experiments(net):
    csvfile = open(network_path[int(sys.argv[1])] + ".csv", 'a')
    logwriter = csv.writer(csvfile, delimiter=',',
                       quotechar='|', quoting=csv.QUOTE_MINIMAL)

    executor = ProcessPoolExecutor(max_workers=32)

    d_bound = shiva.max_degree(net)
    max_degree = shiva.max_degree(net)
    total_triangles = shiva.total_triangles(net)

    original_lps = [None] * 5
    for d in range(5):
        D = d_bound / (2 ** d)
        original_lps[d] = executor.submit(shiva.linear_program_solve, net, D)

    sample_lps = [[None] * 5] * 5
    for d in range(5):
        D = d_bound / (2 ** d)

        for k in range(5):
            p = 1 / (2 ** (k + 1))
            sample_lps[d][k] = experiment(executor, net, D, p)

    for d in range(5):
        D = d_bound / (2 ** d)

        for k in range(5):
            p = 1 / (2 ** (k + 1))
            if sample_lps[d][k] == -1:
                sample_lp = -1
            else:
                sample_lp = sum(x.result() for x in sample_lps[d][k]) \
                    / len(sample_lps[d][k])
            logwriter.writerow([
                                max_degree,
                                total_triangles,
                                D, p,
                                original_lps[d].result(),
                                sample_lp,
                                original_lps[d].result() / sample_lp,
            ])

    executor.shutdown(wait=True)


def run_experiments_average_degree(net, c):
    csvfile = open(network_path[int(sys.argv[1])] + ".c.csv", 'a')
    logwriter = csv.writer(csvfile, delimiter=',',
                       quotechar='|', quoting=csv.QUOTE_MINIMAL)

    executor = ProcessPoolExecutor(max_workers=32)

    average_degree = shiva.average_degree(net)
    max_degree = shiva.max_degree(net)
    total_triangles = shiva.total_triangles(net)

    multipliers = [1.0, 1.5, 2.0]

    original_lps = []
    for d in range(len(multipliers)):
        D = multipliers[d] * average_degree
        original_lps.append(executor.submit(shiva.linear_program_solve, net, D))

    sample_lps = {}

    for d in range(len(multipliers)):
        D = multipliers[d] * average_degree

        for k in range(5):
            p = 1 / (2 ** (k + 1))

            sample_lps[(d, k)] = experiment(executor, net, D, p, c)

            # if k == 0:
            #     print("Now", d, k, sample_lps[(d, k)][0])

    # for d in range(len(multipliers)):
    #     D = multipliers[d] * average_degree

    #     for k in range(5):
    #         p = 1 / (2 ** (k + 1))

    #         if k == 0:
    #             print("NowNow", d, k, sample_lps[(d, k)][0])

    for d in range(len(multipliers)):
        D = multipliers[d] * average_degree

        for k in range(5):
            p = 1 / (2 ** (k + 1))

            if sample_lps[(d, k)] == -1:
                sample_lp = -1
                sample_triangles = -1
            else:
                sample_lp = sum(x.result()[0] for x in sample_lps[(d, k)]) / len(sample_lps[(d, k)])
                sample_triangles = sum(x.result()[1] for x in sample_lps[(d, k)]) / len(sample_lps[(d, k)])

            # temp = [x.result()[0] for x in sample_lps[(d, k)]] 

            # if k == 0:
            #     print("NotNow", d, k, sample_lps[(d, k)][0])
            #     print("Out", d, k, temp) 

            logwriter.writerow([
                                max_degree,
                                total_triangles,
                                D, p,
                                original_lps[d].result(),
                                sample_lp,
                                original_lps[d].result() / sample_lp,
                                sample_triangles,
                                c
            ])

    executor.shutdown(wait=True)


def experiment(executor, net, D, p, c, repeat=None):
    try:
        if repeat is None:
            repeat = int(round(2 * math.log2(net.number_of_nodes())))

        # original_lp = shiva.linear_program_solve(net, D)

        sample_future = []
        for i in range(repeat):
            sample_future.append(executor.submit(shiva_color_sample, net, D, p, c))

        # # All process will join here
        # sample_lp = sum(x.result() for x in sample_future) / repeat

        # csvfile = open(network_path[int(sys.argv[1])] + ".csv", 'a')
        # logwriter = csv.writer(csvfile, delimiter=',',
        #                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # logwriter.writerow([D, p, original_lp, sample_lp, original_lp / sample_lp, shiva.max_degree(net)])

        return sample_future
    except:
        # csvfile = open(network_path[int(sys.argv[1])] + ".csv", 'a')
        # logwriter = csv.writer(csvfile, delimiter=',',
        #                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # logwriter.writerow([D, p, original_lp, -1, -1, shiva.max_degree(net)])
        e = sys.exc_info()[0]
        print("<p>Error: %s</p>" % e)
        return -1


def triangle_dist(net, filename):
    
    list_of_triangles = []
    triangles_per_node = {}

    for i in net.nodes():
        for j in net.neighbors(i):
            for k in net.neighbors(j):
                if i < j and j < k and \
                   net.has_edge(i, k):
                    list_of_triangles.append([i, j, k])
                    if i in triangles_per_node.keys():
                        triangles_per_node[i] += 1
                    else:
                        triangles_per_node[i] = 1
                    if j in triangles_per_node.keys():
                        triangles_per_node[j] += 1
                    else:
                        triangles_per_node[j] = 1
                    if k in triangles_per_node.keys():
                        triangles_per_node[k] += 1
                    else:
                        triangles_per_node[k] = 1

    try:
        csvfile = open(network_path[int(sys.argv[1])] + filename + ".csv", 'a')
        logwriter = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        print(filename)
        print(len(triangles_per_node))
        for node, triangle_count in triangles_per_node.items():
            logwriter.writerow([node, triangle_count])

    except:
        # csvfile = open(network_path[int(sys.argv[1])] + ".csv", 'a')
        # logwriter = csv.writer(csvfile, delimiter=',',
        #                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # logwriter.writerow([D, p, original_lp, -1, -1, shiva.max_degree(net)])
        e = sys.exc_info()[0]
        print("<p>Error: %s</p>" % e)


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

    # # Run experiment
    # for c in [0, 1, 2, 4, 8, 16, 32]:
    #     run_experiments_average_degree(net, c)

    for c in [1, 2, 4, 8, 16, 32]:
        print(1/c)
        triangle_dist(color_sample(net, 1/c), ".distribution." + str(c))


if __name__ == "__main__":
    main()
