import networkx as nx
# import gurobipy as grb
import numpy as np
import math
import random
import csv
import sys
import common
from concurrent.futures import ProcessPoolExecutor
import timeit

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


def max_common_neighbors(net):
    max_common_neighbors_count = -1

    for i in net.nodes():
        if net.degree(i) < max_common_neighbors_count:
            continue
        for j in net.nodes():
            if i > j:
                continue
            if net.degree(j) < max_common_neighbors_count:
                continue
            common_neighbors = len(set(net.neighbors(i)).intersection(net.neighbors(j)))
            if common_neighbors > max_common_neighbors_count:
                max_common_neighbors_count = common_neighbors

    return max_common_neighbors_count


def karwa_local_sensitivity(net, epsilon, delta, repeat=1):
    ls = max_common_neighbors(net)

    beta_arr = np.random.laplace(0, 1/epsilon, repeat) + math.log(math.exp(epsilon) + 1 / delta) / epsilon + ls

    result_arr = [(common.triangle_count(net)[0] + np.random.laplace(0, beta_hat / epsilon)) for beta_hat in beta_arr]

    if repeat == 1:
        return result_arr[0]

    return result_arr


def local_sensitivity_color_sample(net, p, epsilon, delta):
    print("****************************************", p, epsilon, delta)

    sampled_net = color_sample(net, p)

    return karwa_local_sensitivity(sampled_net, epsilon, delta) / (p**2)


# TODO: Fix run experiment
def run_experiments(net, K, epsilon, delta, workers=4, repeat=10):
    csvfile = open(network_path[int(sys.argv[1])] + ".csv", 'a')
    logwriter = csv.writer(csvfile, delimiter=',',
                       quotechar='|', quoting=csv.QUOTE_MINIMAL)

    executor = ProcessPoolExecutor(max_workers=workers)

    total_triangles = common.triangle_count(net)[0]

    runtime_average = runtime(net, [1] + K)
    # d_bound = shiva.max_degree(net)
    # max_degree = shiva.max_degree(net)
    # total_triangles = shiva.total_triangles(net)

    # Submit Karwa impl 
    karwa_results = executor.submit(karwa_local_sensitivity, net, epsilon, delta, repeat=repeat)

    # Submit sampling batches
    sample_results = {} 
    for k in K:
        p = 1 / (2 ** (k - 1))
        sample_results[k] = experiment(executor, net, p, epsilon, delta, repeat=repeat)

    # Results for Karwa impl
    sample_mean = np.average(karwa_results.result())
    sample_std = np.std(karwa_results.result())
    logwriter.writerow([total_triangles, 1, epsilon, delta, sample_mean, sample_std, runtime_average[1]])

    # Results for sampling impl
    for k in K:
        p = 1 / (2 ** (k - 1))
        if sample_results[k] == -1:
            sample_mean = -1
            sample_std = -1
        else:
            sample_mean = sum(x.result() for x in sample_results[k]) \
                / len(sample_results[k])
            sample_std = np.std([x.result() for x in sample_results[k]])
        logwriter.writerow([total_triangles, k, epsilon, delta, sample_mean, sample_std, runtime_average[k]])


    executor.shutdown(wait=True)


def runtime(net, K, epsilon=0.1, delta=0.00001, repeat=5):
    runtime_average = {} 
    for k in K:
        p = 1 / (2 ** (k - 1))
        time_k = 0
        for i in range(repeat):
            start = timeit.default_timer()
            if k == 1:
                karwa_local_sensitivity(net, epsilon, delta)
            else:
                local_sensitivity_color_sample(net, p, epsilon, delta)
            end = timeit.default_timer()
            time_k += (end - start)
        runtime_average[k] = time_k / repeat
    return runtime_average


def experiment(executor, net, p, epsilon, delta, repeat=None):
    try:
        if repeat is None:
            repeat = int(round(2 * math.log2(net.number_of_nodes())))

        # original_lp = shiva.linear_program_solve(net, D)

        sample_future = []
        for i in range(repeat):
            sample_future.append(executor.submit(local_sensitivity_color_sample, net, p, epsilon, delta))

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


# def run_experiments_degree(net, c):
#     csvfile = open(network_path[int(sys.argv[1])] + ".c.csv", 'a')
#     logwriter = csv.writer(csvfile, delimiter=',',
#                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
# 
#     executor = ProcessPoolExecutor(max_workers=32)
# 
#     average_degree = shiva.average_degree(net)
#     max_degree = shiva.max_degree(net)
#     total_triangles = shiva.total_triangles(net)
# 
#     multipliers = [1.0, 1.5, 2.0]
# 
#     original_lps = []
#     for d in range(len(multipliers)):
#         D = multipliers[d] * average_degree
#         original_lps.append(executor.submit(shiva.linear_program_solve, net, D))
# 
#     sample_lps = {}
# 
#     for d in range(len(multipliers)):
#         D = multipliers[d] * average_degree
# 
#         for k in range(5):
#             p = 1 / (2 ** (k + 1))
# 
#             sample_lps[(d, k)] = experiment(executor, net, D, p, c)
# 
#             # if k == 0:
#             #     print("Now", d, k, sample_lps[(d, k)][0])
# 
#     # for d in range(len(multipliers)):
#     #     D = multipliers[d] * average_degree
# 
#     #     for k in range(5):
#     #         p = 1 / (2 ** (k + 1))
# 
#     #         if k == 0:
#     #             print("NowNow", d, k, sample_lps[(d, k)][0])
# 
#     for d in range(len(multipliers)):
#         D = multipliers[d] * average_degree
# 
#         for k in range(5):
#             p = 1 / (2 ** (k + 1))
# 
#             if sample_lps[(d, k)] == -1:
#                 sample_lp = -1
#                 sample_triangles = -1
#             else:
#                 sample_lp = sum(x.result()[0] for x in sample_lps[(d, k)]) / len(sample_lps[(d, k)])
#                 sample_triangles = sum(x.result()[1] for x in sample_lps[(d, k)]) / len(sample_lps[(d, k)])
# 
#             # temp = [x.result()[0] for x in sample_lps[(d, k)]] 
# 
#             # if k == 0:
#             #     print("NotNow", d, k, sample_lps[(d, k)][0])
#             #     print("Out", d, k, temp) 
# 
#             logwriter.writerow([
#                                 max_degree,
#                                 total_triangles,
#                                 D, p,
#                                 original_lps[d].result(),
#                                 sample_lp,
#                                 original_lps[d].result() / sample_lp,
#                                 sample_triangles,
#                                 c
#             ])
# 
#     executor.shutdown(wait=True)

# def triangle_dist(net, filename):
#     
#     list_of_triangles = []
#     triangles_per_node = {}
# 
#     for i in net.nodes():
#         for j in net.neighbors(i):
#             for k in net.neighbors(j):
#                 if i < j and j < k and \
#                    net.has_edge(i, k):
#                     list_of_triangles.append([i, j, k])
#                     if i in triangles_per_node.keys():
#                         triangles_per_node[i] += 1
#                     else:
#                         triangles_per_node[i] = 1
#                     if j in triangles_per_node.keys():
#                         triangles_per_node[j] += 1
#                     else:
#                         triangles_per_node[j] = 1
#                     if k in triangles_per_node.keys():
#                         triangles_per_node[k] += 1
#                     else:
#                         triangles_per_node[k] = 1
# 
#     try:
#         csvfile = open(network_path[int(sys.argv[1])] + filename + ".csv", 'a')
#         logwriter = csv.writer(csvfile, delimiter=',',
#                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
#         print(filename)
#         print(len(triangles_per_node))
#         for node, triangle_count in triangles_per_node.items():
#             logwriter.writerow([node, triangle_count])
# 
#     except:
#         # csvfile = open(network_path[int(sys.argv[1])] + ".csv", 'a')
#         # logwriter = csv.writer(csvfile, delimiter=',',
#         #                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
#         # logwriter.writerow([D, p, original_lp, -1, -1, shiva.max_degree(net)])
#         e = sys.exc_info()[0]
#         print("<p>Error: %s</p>" % e)


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

    # Run experiment
    epsilon = 0.1
    delta = 1 / net.number_of_edges()

    K = [2, 4, 8, 16, 32]
    run_experiments(net, K, epsilon, delta, workers=int(sys.argv[2]),repeat=100)

    # for c in [1, 2, 4, 8, 16, 32]:
    #     print(1/c)
    #     triangle_dist(color_sample(net, 1/c), ".distribution." + str(c))


if __name__ == "__main__":
    main()
