#!/usr/bin/env python3

import networkx as nx
import matplotlib.pyplot as plt
import random


node_num = 15

dag = nx.DiGraph()

for i in range(node_num):
    dag.add_node(i)

for u in range(node_num):
    possible_targets = [v for v in range(node_num) if u != v and not dag.has_edge(v, range(node_num))]
    if possible_targets:
        v = random.choice(possible_targets)
        dag.add_edge(u, v)
        print(f"node : {u} has edge with : {v}")

print("done")

nx.draw(dag, with_labels=True, arrows=True)
plt.show()
