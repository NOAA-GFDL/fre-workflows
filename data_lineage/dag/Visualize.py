import matplotlib.pyplot as plt
import networkx as nx


def draw_helper(dag):
    pos = nx.fruchterman_reingold_layout(G=dag)
    args = {
        'with_labels': True,
        'arrows': True,
        'node_size': 500,
        'node_color': 'skyblue',
        'font_size': 8,
        'font_weight': 'bold',
        'arrowsize': 20
    }
    nx.draw(dag, pos, **args)

    print("Finished drawing dag, closing the graph window will terminate the program.")
    plt.show()


def draw(my_dag):
    nodes = my_dag.get_nodes()

    dag = nx.MultiDiGraph()

    for node in nodes:
        if 'remap-pp-components' not in node.get_name():
            name = node.get_name()
            dag.add_node(name)

    for edge in my_dag.get_edges():
        start = edge.get_start().get_name()
        end = edge.get_end().get_name()
        if dag.has_edge(start, end):
            continue
        else:
            dag.add_edge(start, end)

    draw_helper(dag)

