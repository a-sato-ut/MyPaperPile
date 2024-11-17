import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt 
import math


def normalize_title(title):
    title = title.lower()
    title = title[0].upper() + title[1:]
    return title

def is_same_title(title1, title2):
    if normalize_title(title1) == normalize_title(title2):
        return True
    # remove special characters
    title1 = ''.join(e for e in title1 if e.isalnum())
    title2 = ''.join(e for e in title2 if e.isalnum())
    if title1 == title2:
        return True
    # calc longest common substring
    dp = [[0] * (len(title2) + 1) for _ in range(len(title1) + 1)]
    max_len = 0
    for i in range(1, len(title1) + 1):
        for j in range(1, len(title2) + 1):
            if title1[i - 1] == title2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                max_len = max(max_len, dp[i][j])
    return max_len >= 0.9 * max(len(title1), len(title2))

def get_common_references(references_dict):
    common_references = {}
    for folder, references in references_dict.items():
        for reference in references:
            title = reference['title']
            if title not in common_references:
                common_references[title] = []
            common_references[title].append(folder)

    # extract common references
    common_references = {k: v for k, v in common_references.items() if len(v) > 1}

    # merge similar titles
    to_be_merged_titles = []
    for title in list(common_references.keys()):
        for other_title in list(common_references.keys()):
            if title == other_title:
                continue
            if is_same_title(title, other_title):
                to_be_merged_titles.append((title, other_title))

    # list of sets
    connected_components = []
    for title1, title2 in to_be_merged_titles:
        found = False
        for component in connected_components:
            if title1 in component or title2 in component:
                component.add(title1)
                component.add(title2)
                found = True
                break
        if not found:
            connected_components.append({title1, title2})

    # for connected_component in connected_components:
    #     print("[INFO] Connected components:", connected_component)

    for component in connected_components:
        if len(component) == 1:
            continue
        new_title = max(component, key=len)
        for title in component:
            if title == new_title:
                continue
            common_references[new_title] += common_references[title]
            del common_references[title]

    return common_references

def visualize_common_references(graph, labels):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(24, 24))
    
    # Draw nodes with a different color for folders and references
    nx.draw_networkx_nodes(graph, pos, node_size=500, node_color='lightblue')
    nx.draw_networkx_edges(graph, pos, alpha=0.5, edge_color='gray')
    nx.draw_networkx_labels(graph, pos, labels, font_size=8)

    plt.title("Common References Network")
    plt.savefig('fig/common_references_network.pdf')
    plt.close()

    # 連結成分ごとに描画
    connected_components = list(nx.connected_components(graph))
    for i, component in enumerate(connected_components):
        subgraph = graph.subgraph(component)
        sub_labels = {node: labels[node] for node in component}
        pos = nx.spring_layout(subgraph)
        plt.figure(figsize=(24, 24))
        nx.draw_networkx_nodes(subgraph, pos, node_size=500, node_color='lightblue')
        nx.draw_networkx_edges(subgraph, pos, alpha=0.5, edge_color='gray')
        nx.draw_networkx_labels(subgraph, pos, sub_labels, font_size=8)
        plt.title(f"Connected Component {i}")
        plt.savefig(f'fig/connected_component_{i}.pdf')
        plt.close()

def visualize_common_references_year(graph, labels, references_dict):
    # 連結成分ごとに描画
    connected_components = list(nx.connected_components(graph))
    for i, component in enumerate(connected_components):
        subgraph = graph.subgraph(component)
        sub_labels = {node: labels[node] for node in component}
        pos = nx.spring_layout(subgraph)

        years = {}
        for node in subgraph.nodes:
            year = ""
            for di in references_dict:
                for reference in references_dict[di]:
                    if reference['title'] == node:
                        year = reference['year']
                        break
                if year != "":
                    break
            if year == "":
                year = "2025"
            try:
                years[node] = int(year)
            except:
                years[node] = 2025

        for node in subgraph.nodes:
            # pos[node][0] = years[node]
            pos[node][0] = - math.log(2026 - years[node])

        plt.figure(figsize=(24, 24))
        nx.draw_networkx_nodes(subgraph, pos, node_size=500, node_color='lightblue')
        nx.draw_networkx_edges(subgraph, pos, alpha=0.5, edge_color='gray')
        nx.draw_networkx_labels(subgraph, pos, sub_labels, font_size=8)
        plt.xlabel('Year')
        plt.title(f"Connected Component {i}")
        plt.savefig(f'fig/connected_component_{i}_year.pdf')
        plt.close()

if __name__ == '__main__':
    # mkdir fig 
    os.makedirs('fig', exist_ok=True)

    # load references
    paper_folder = 'paper'
    references_dict = {}
    for folder in os.listdir(paper_folder):
        folder_path = os.path.join(paper_folder, folder)
        if not os.path.isdir(folder_path):
            continue
        references_folder = os.path.join(folder_path, 'references')
        references_csv = os.path.join(references_folder, 'references.csv')
        if not os.path.exists(references_csv):
            continue
        references = pd.read_csv(references_csv)
        references = references.dropna(subset=['title'])
        references.to_csv(references_csv, index=False)

        references_dict[folder] = references.to_dict(orient='records')

    common_references = get_common_references(references_dict)
    # print(f"Common references ({len(common_references)}):")
    # for title in sorted(common_references.keys()):
    #     print(f'[COMMON] {title}: {len(common_references[title])}')

    # visualize the network
    G = nx.Graph()
    for title, folders in common_references.items():
        G.add_node(title)
        for folder in folders:
            G.add_edge(title, folder)

    pos = nx.spring_layout(G)
    MAX_LABEL_LENGTH = 20
    labels = {
        node: (node if len(node) <= MAX_LABEL_LENGTH else node[:MAX_LABEL_LENGTH] + '...') 
        for node in G.nodes
    }
    visualize_common_references(G, labels)
    visualize_common_references_year(G, labels, references_dict)
