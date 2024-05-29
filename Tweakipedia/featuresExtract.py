from nltk.corpus import stopwords
import wikipedia
import requests
import json
from datetime import datetime
import pandas as pd
import copy
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import numpy as np
import sys
import networkx as nx
import csv



# nltk.download('punkt')
# nltk.download('stopwords')
_DEBUG_ = False
stop_words = set(stopwords.words('english'))
porter = PorterStemmer()


def extractPageSize(headers):
    pages = [wikipedia.page(name, auto_suggest=False) for name in headers]
    return [len(stemSentence(page.content)) for page in pages]


##############################################################

# This method reads the graph structure from the input file
def buildG(G, file_, delimiter_):
    # construct the weighted version of the contact graph from cgraph.dat file
    # reader = csv.reader(open("/home/kazem/Data/UCI/karate.txt"), delimiter=" ")
    reader = csv.reader(open(file_), delimiter=delimiter_)
    for line in reader:
        if len(line) > 2:
            if float(line[2]) != 0.0:
                # line format: u,v,w
                G.add_edge(int(line[0]), int(line[1]), weight=float(line[2]))
        else:
            # line format: u,v
            G.add_edge(int(line[0]), int(line[1]), weight=1.0)


# This method keeps removing edges from Graph until one of the connected components of Graph splits into two
# compute the edge betweenness
def CmtyGirvanNewmanStep(G):
    if _DEBUG_:
        print("Running CmtyGirvanNewmanStep method ...")
    init_ncomp = nx.number_connected_components(G)  # no of components
    ncomp = init_ncomp
    while ncomp <= init_ncomp:
        bw = nx.edge_betweenness_centrality(G, weight='weight')  # edge betweenness for G
        # find the edge with max centrality
        if bw.values():
            max_ = max(bw.values())
        else:
            break
        # find the edge with the highest centrality and remove all of them if there is more than one!
        for k, v in bw.items():
            if float(v) == max_:
                G.remove_edge(k[0], k[1])  # remove the central edge
        ncomp = nx.number_connected_components(G)  # recalculate the no of components


# This method compute the modularity of current split
def _GirvanNewmanGetModularity(G, deg_, m_):
    New_A = nx.adj_matrix(G)
    New_deg = {}
    New_deg = UpdateDeg(New_A, G.nodes())
    # Let's compute the Q
    comps = nx.connected_components(G)  # list of components
    # print('No of communities in decomposed G: {}'.format(nx.number_connected_components(G)))
    Mod = 0  # Modularity of a given partitionning
    for c in comps:
        EWC = 0  # no of edges within a community
        RE = 0  # no of random edges
        for u in c:
            EWC += New_deg[u]
            RE += deg_[u]  # count the probability of a random edge
        Mod += (float(EWC) - float(RE * RE) / float(2 * m_))
    Mod = Mod / float(2 * m_)
    if _DEBUG_:
        print("Modularity: {}".format(Mod))
    return Mod


def UpdateDeg(A, nodes):
    deg_dict = {}
    n = len(nodes)  # len(A) ---> some ppl get issues when trying len() on sparse matrixes!
    B = A.sum(axis=1)
    i = 0
    for node_id in list(nodes):
        deg_dict[node_id] = B[i, 0]
        i += 1
    return deg_dict


# This method runs GirvanNewman algorithm and find the best community split by maximizing modularity measure
def runGirvanNewman(G, Orig_deg, m_):
    # let's find the best split of the graph
    BestQ = 0.0
    Q = 0.0
    while True:
        CmtyGirvanNewmanStep(G)
        Q = _GirvanNewmanGetModularity(G, Orig_deg, m_);
        # print("Modularity of decomposed G: {}".format(Q))
        if Q > BestQ:
            BestQ = Q
            Bestcomps = list(nx.connected_components(G))  # Best Split
            # print("Identified components: {}".format(Bestcomps))
        if G.number_of_edges() == 0:
            break
    if BestQ > 0.0:
        # print("Max modularity found (Q): {} and number of communities: {}".format(BestQ, len(Bestcomps)))
        # print("Graph communities: {}".format(Bestcomps))
        pass
    else:
        # print("Max modularity (Q):", BestQ)
        pass
    return Bestcomps


def find_com(f, page_dict):

    G = nx.Graph()  # let's create the graph first
    buildG(G, f, ',')

    if _DEBUG_:
        print('G nodes: {} & G no of nodes: {}'.format(G.nodes(), G.number_of_nodes()))

    n = G.number_of_nodes()  # |V|
    A = nx.adj_matrix(G)  # adjacenct matrix

    m_ = 0.0  # the weighted version for number of edges
    for i in range(0, n):
        for j in range(0, n):
            m_ += A[i, j]
    m_ = m_ / 2.0
    if _DEBUG_:
        print("m: {}".format(m_))

    # calculate the weighted degree for each node
    Orig_deg = {}
    Orig_deg = UpdateDeg(A, G.nodes())

    # run Newman alg
    comps = runGirvanNewman(G, Orig_deg, m_)
    comps_by_names = []
    for comp in comps:
        comps_by_names.append([page_dict[node] for node in comp])

    # print(comps_by_names)
    return comps_by_names

##############################################################

def get_cosine_sim(strs, threshold):
    vect = TfidfVectorizer(min_df=1, stop_words="english")
    tfidf = vect.fit_transform(strs)
    pairwise_similarity = tfidf * tfidf.T
    for i in range(pairwise_similarity.data.size):
        pairwise_similarity.data[i] = int(pairwise_similarity.data[i] >= threshold)
    return pairwise_similarity.toarray()


def stemSentence(sentence):
    token_words = word_tokenize(sentence)
    token_words = [w for w in token_words if not w.lower() in stop_words]
    stem_sentence = []
    for word in token_words:
        stem_sentence.append(porter.stem(word))
        stem_sentence.append(" ")
    return "".join(stem_sentence)


def make_sim_mat_file( headers, threshold):
    pages = [wikipedia.page(name, auto_suggest=False) for name in headers]
    am = get_cosine_sim([stemSentence(page.summary) for page in pages],
                        threshold)
    df = pd.DataFrame(data=am, index=headers, columns=headers)
    # mat = df.to_csv(query + "_sim_mat", sep='\t')
    # return mat
    return df


def findCommunites( headers, threshold):
    sim_mat = make_sim_mat_file( headers, threshold)
    df_np = sim_mat.to_numpy()
    # page_dict = df_np[:, 0]
    arr = np.logical_or(df_np, df_np.T)
    file1 = open("graph.txt", "a")
    file1.truncate(0)
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if arr[i][j] == 1 and i <= j:
                file1.write(str(i) + "," + str(j) + ",1" + "\n")

    file1.close()
    coms = find_com(file1.name, headers)
    total_vec = []
    for name in headers:
        vec = [1 if name in coms[i] else 0 for i in range(len(coms))]
        total_vec.append(vec)
    return total_vec



# findCommunites( hedears,0.1)
