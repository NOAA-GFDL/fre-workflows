import matplotlib.pyplot as plt
import networkx as nx


def draw_helper(dag):
    pos = nx.planar_layout(dag)
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

    plt.title("Directed Acyclic Graph for am5_c96L33_amip/run52")
    print("Finished drawing dag, closing the graph window will terminate the program.")
    plt.show()


def draw(my_dag):
    dag = nx.MultiDiGraph()

    nodes = my_dag.get_nodes()
    for node in nodes:
        name = node.get_name().split('0101T0000')[0]
        dag.add_node(name)

    for edge in my_dag.get_edges():
        start = edge.get_start().get_name().split('0101T0000')[0]
        end = edge.get_end().get_name().split('0101T0000')[0]
        if dag.has_edge(start, end):
            continue
        else:
            dag.add_edge(start, end)

    draw_helper(dag)

