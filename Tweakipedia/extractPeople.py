import item as item
import requests
from bs4 import BeautifulSoup
import wikipedia
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.axis as ax
import collections

people_pages = []
n = 100  # number of pages to extract


def extractPeoplePages(url, DB):
    """
    creating DB of pages by category: this methods parses names of pages from url,
    taking some randomly and writes them to DB (overall at least n pages)
    :param url: url to begin extraction
    :param DB: file to store names
    :return: none
    """
    if len(people_pages) >= n:
        return
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    table = soup.find('div', attrs={'id': 'bodyContent'})
    rows = table.findAll('div', attrs={'class': 'mw-category mw-category-columns'})[0].text.split("\n")[1:]
    # rows = random.sample(rows, 10)
    x = random.choice(rows)
    # people_pages.extend(rows)
    people_pages.append(x)
    with open(DB, "a", encoding='utf-8') as f:
        f.write("to del: " + url + "\n")
        # x = "\n".join(rows)
        f.write(x)
        f.write("\n")

    url = ""
    i = 0
    while i < 50:
        next = False
        for a in soup.find_all('a', href=True):
            if a.text == "next page":
                next = a
                break
        if next:
            url = "https://en.wikipedia.org" + str(next).split('"')[1].replace("amp;", "")
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            i += 1
    extractPeoplePages(url)

# extractPeoplePages('https://en.wikipedia.org/w/index.php?title=Category:Living_people&pagefrom=Bhatti%2C+Mukhtar%0AMukhtar+Bhatti#mw-pages', "peopleDB1")

# def deleteLines(f1, f2):
#     with open(f1, "r", encoding='utf-8') as f1:
#         lines = f1.readlines()
#
#     bool = True
#     lines_ = []
#     for line in lines:
#         if not bool:
#             lines_.append(line)
#         bool = not bool
#
#     with open(f2, "a", encoding='utf-8') as f2:
#         x = "".join(lines_)
#         f2.write(x)
#
#
# deleteLines("peopleDB2", "peopleDB3")
