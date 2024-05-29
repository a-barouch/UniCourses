import wikipedia
import pandas as pd
import numpy as np
import random

def buildAdjFromStarter(MAIN_PAGE):
    """
    create an adjacency matrix from a starting page within its neighbors
    :return: adjacency matrix
    """
    # wikipedia page object is created
    page_object = wikipedia.page(MAIN_PAGE, auto_suggest=False)
    title = page_object.original_title

    # how many links the page is referencing to within wikipedia
    orig_links = page_object.links
    len_links = len(orig_links)
    print(len_links)

    am = pd.DataFrame(np.zeros(shape=(len_links, len_links)), columns=orig_links, index=orig_links)

    # run over links from page and build adjacency matrix within themselves
    for link in orig_links:
        try:
            linked_page = wikipedia.page(link, auto_suggest=False)
            intersection = list(set(orig_links) & set(linked_page.links))
            for i in range(len_links):
                am[link][i] = (orig_links[i] in intersection)
            print(linked_page.title)
        except:
            continue

    am.to_csv(title + "_links.csv", sep='\t')
    return am

def buildAdjMat(headers):
    '''
    create adjacency matrix from given names of pages
    :param headers: pages names
    :return: adjacency matrix
    '''
    number_of_pages  = len(headers)
    am = pd.DataFrame(np.zeros(shape=(number_of_pages, number_of_pages), dtype=int), columns=headers, index=headers)

    pages_links = {header : wikipedia.page(header, auto_suggest=False).links for header in headers}
    for header in headers:
        for linked in pages_links[header]:
            if linked in headers:
                am[header][linked] = 1
    am.to_csv(str(random.randrange(9000)+1000) + "_links.csv", sep='\t')
    return am

#
# if __name__ == '__main__':
#     buildAdjMat(["Biology","Genetics","Rhesus macaque","Pelican","Jane Goodall",
#                  "Hemoglobin","Cancer","RNA","Virus","Evolution","Plant","amino acids",
#                  "Arabidopsis","Coronavirus","Chimpanzee","Primates"])