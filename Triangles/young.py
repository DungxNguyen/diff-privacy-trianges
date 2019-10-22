# Dung Nguyen
# Implementation of young algorithm for counting triangles
import networkx as nx
import gurobipy as grb
import numpy as np
import math
import random
import shiva

network_path = "../data_graphs/ca-GrQc.txt"



def main():
    net = nx.read_edgelist(network_path, create_using=nx.Graph(), nodetype=int)
    

if __name__ == "__main__":
    main()
