import matplotlib.pyplot as plt
import networkx as nx
import dag_create as create


def draw(dag):
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


def traverse_dag(dag, edge_dict):
    print(f'---DAG Stats---')
    print(f'Number of nodes: {len(dag.nodes)}')
    print(f'Number of edges: {len(dag.edges)}')
    print(f'Is Acyclic? {str(nx.is_directed_acyclic_graph(dag))}')
    for node in dag.nodes():
        print(f'\nLooking at node {node}')
        edges = dag.edges(node, data=True)
        if edges:
            print(f'{node} shares an edge with')
            for next_job in edges:
                next_job_name = next_job[1]
                edge_link = (node, next_job_name)
                edge_files = edge_dict[edge_link]
                weight = dag[node][next_job_name][0]["weight"]
                print(f'    ╰ {next_job[1]} with a weight of {weight}')
                for file in edge_files:
                    print(f'        ├ {file}')
        else:
            print(f'{node} does not share any edges')
    print('\nFinished traversing dag')
    return 0


def main():
    job_dict = create.fetch.main()
    dag, edge_dict = create.create_dag(job_dict)
    traverse_dag(dag, edge_dict)
    draw(dag)


if __name__ == "__main__":
    main()
