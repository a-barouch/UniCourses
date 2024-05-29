import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from random import randint

FILENAME = "countries"
import random


def read_adjacency(filename, cosine=False):
    df = pd.read_csv(filename, sep=",", index_col=False)
    # list_of_column_names = list(df.columns)[1:]
    df.set_index('Unnamed: 0', inplace=True)
    if cosine:
        df.values[[np.arange(df.shape[0])] * 2] = 0
    return df


def plot_graph(df, comps=None):
    # create graph from adjacency matrix
    G = nx.from_pandas_adjacency(df, create_using=nx.DiGraph)

    # remove communities of 1 node
    if comps:
        pass
        comps = [comp for comp in comps if len(comp) > 1]
        nodes_to_leave = [item for sublist in comps for item in sublist]
        nodes_to_remove = [x for x in G.nodes if x not in nodes_to_leave]  # nodes not in community
        G.remove_nodes_from(nodes_to_remove)
    else:  # remove nodes with low degree
        nodes_to_remove = [node for node, degree in dict(G.degree()).items() if degree < 5]
        G.remove_nodes_from(nodes_to_remove)
        nodes_to_remove2 = [node for node, degree in dict(G.degree()).items() if node.startswith("Glossary")]

        G.remove_nodes_from(nodes_to_remove2)
    # plotting graph
    # G.remove_edges_from(list(G.edges()))
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos, with_labels=False, width=0.4)
    # node_size=[v * 100 for v in d.values()]) # size by degree

    labels = {}
    # add node label with a probability of 0.1
    for node in G.nodes():
        if random.random() < 0.1:
            # set the node name as the key and the label as its value
            labels[node] = node

    # color componenets of a community with the same color
    if comps:
        colors = get_colors(len(comps))
        i = 0
        for comp in comps:
            nx.draw_networkx_nodes(G, pos, nodelist=comp, node_color=[colors[i] for j in range(len(comp))])
            i += 1
        nx.draw_networkx_labels(G, pos, labels, font_size=8)

    plt.title(FILENAME+" community plot")
    plt.savefig(FILENAME + '.png')
    plt.show()


# create a list on n different colors
def get_colors(n):
    # randomly generate n colors
    # colors = []
    # for i in range(n):
    #     colors.append('#%06X' % randint(0, 0xFFFFFF))

    # get fixed colors
    colors = ["lightcoral", "lime", "gold", "magenta", "blueviolet", "lightsteelblue", "turquoise"]
    return colors

# read list of lists of communities by name of nodes
def get_communities():
    import pickle
    with open("communities_" + FILENAME + ".txt", "rb") as new_filename:
        pp = pickle.load(new_filename)
    return pp


# read communities as one hot encoded matrix
def get_communities2(names):
    import json
    with open(FILENAME + "_communities.txt") as f:
        lst = json.load(f)
    comps = [[] for i in range(len(names))]
    for idx in range(len(names)):
        try:
            comp_index = lst[idx].index(1)
            comps[comp_index].append(names[idx])
        except:
            continue
    return comps


if __name__ == '__main__':
    comps = None
    df = read_adjacency(filename=FILENAME + '_links.csv', cosine=False)
    comps = get_communities()

    # names = ['China', 'India', 'United States', 'Indonesia', 'Pakistan', 'Brazil', 'Nigeria', 'Bangladesh', 'Russia', 'Mexico', 'Japan', 'Ethiopia', 'Philippines', 'Egypt', 'Vietnam', 'DR Congo', 'Iran', 'Turkey', 'Germany', 'France', 'United Kingdom', 'Thailand', 'South Africa', 'Tanzania', 'Italy', 'Myanmar', 'South Korea', 'Colombia', 'Kenya', 'Spain', 'Argentina', 'Algeria', 'Sudan', 'Uganda', 'Iraq', 'Ukraine', 'Canada', 'Poland', 'Morocco', 'Uzbekistan', 'Saudi Arabia', 'Peru', 'Afghanistan', 'Malaysia', 'Angola', 'Mozambique', 'Ghana', 'Yemen', 'Nepal', 'Venezuela', 'Ivory Coast', 'Madagascar', 'Australia', 'North Korea', 'Cameroon', 'Niger', 'Sri Lanka', 'Burkina Faso', 'Mali', 'Chile', 'Romania', 'Kazakhstan', 'Malawi', 'Zambia', 'Syria', 'Ecuadorians', 'Netherlands', 'Senegal', 'Guatemala', 'Chad', 'Somalia', 'Zimbabwe', 'Cambodia', 'South Sudan', 'Rwanda', 'Guinea', 'Burundi', 'Benin', 'Bolivia', 'Tunisia', 'Haiti', 'Belgium', 'Cuba', 'Jordan', 'Greece', 'Dominican Republic', 'Czech Republic', 'Sweden', 'Portugal', 'Azerbaijan', 'Hungary', 'Honduras', 'Tajikistan', 'United Arab Emirates', 'Israel', 'Belarus', 'Papua New Guinea', 'Austria', 'Switzerland', 'Sierra Leone', 'Togo', 'Paraguay', 'Laos', 'Libya', 'Serbia', 'El Salvador', 'Lebanon', 'Kyrgyzstan', 'Nicaragua', 'Bulgaria', 'Turkmenistan', 'Denmark', 'Congo', 'Central African Republic', 'Finland', 'Singapore', 'Slovakia', 'Norway', 'Palestine', 'Costa Rica', 'New Zealand', 'Ireland', 'Kuwait', 'Liberia', 'Oman', 'Panama', 'Mauritania', 'Croatia', 'Georgia', 'Eritrea', 'Uruguay', 'Mongolia', 'Bosnia and Herzegovina', 'Armenia', 'Albania', 'Qatar', 'Lithuania', 'Jamaica', 'Moldova', 'Namibia', 'Demographics of the Gambia', 'Botswana', 'Gabon', 'Lesotho', 'Slovenia', 'Latvia', 'North Macedonia', 'Guinea-Bissau', 'Equatorial Guinea', 'Bahrain', 'Trinidad and Tobago', 'Estonia', 'East Timor', 'Mauritius', 'Eswatini', 'Djibouti', 'Fiji', 'Cyprus', 'Comoros', 'Bhutan', 'Guyana', 'Solomon Islands', 'Luxembourg', 'Montenegro', 'Suriname', 'Cape Verde', 'Malta', 'Belize', 'Brunei', 'Demographics of the Bahamas', 'Maldives', 'Iceland', 'Vanuatu', 'Barbados', 'São Tomé and Príncipe', 'Samoa', 'Saint Lucia', 'Kiribati', 'Grenada', 'Saint Vincent and the Grenadines', 'Micronesia', 'Tonga', 'Antigua and Barbuda', 'Seychelles', 'Andorra', 'Dominica', 'Marshall Islands', 'Saint Kitts and Nevis', 'Liechtenstein', 'Monaco', 'San Marino', 'Palau', 'Nauru', 'Tuvalu', 'Vatican City']
    # comps = get_communities2(names)
    plot_graph(df, comps)
