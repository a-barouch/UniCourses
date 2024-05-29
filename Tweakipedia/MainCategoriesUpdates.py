import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from updates import updatesSinceMain, WikiHelper
import json
from plotData import plotUpdates, plotUpdates2


# This file contains the functions that extract the Main topic articles from Wikipedia and their updates
# Scraps the page "https://en.wikipedia.org/wiki/Category:Main_topic_articles" and extracts the Main topic articles titles and links .
def getMainTopicsArticles():
    r = requests.get("https://en.wikipedia.org/wiki/Category:Main_topic_articles")
    soup = BeautifulSoup(r.content, "html.parser")
    cat_divs = soup.find_all("div", class_="mw-category-group")
    page_links = []
    page_titles = []
    for cat_div in cat_divs:
        for a in cat_div.find_all("a"):
            page_links.append(urljoin(r.url, a['href']))
            page_titles.append(a['title'])
    return page_links, page_titles


# finds the Main topic articles updates and cuts them according to the thresholds and saves them in json file (and return them as well)
# we used the json files later to plot the data
def generateMainArticlesUpdateData(thresholds=[210], jsonFileName=None):  # generateMainArticlesUpdateData
    page_links, page_titles = getMainTopicsArticles()
    # page_links = page_links[:5]
    # page_titles = page_titles[:5]
    print("Done collecting main topics articles links and titles.")
    since_ = datetime.now()
    since_ = datetime(since_.year - 5, since_.month, 1)
    pages_updates, pages_bytes = updatesSinceMain(page_links, since_)
    pages_threshold = {}
    for threshold in thresholds:
        pages_threshold[threshold] = []
        for a, b in zip(pages_updates, pages_bytes):
            x, y = WikiHelper.cut_bytes(a, b, threshold=threshold)
            pages_threshold[threshold].append(len(y))
    # print(pages_threshold)
    # print("Done collecting main topics updates.")
    datas = {}
    for j in range(len(thresholds)):
        threshold = thresholds[j]
        data = []
        # print("THRESHOLD: ", threshold)
        for i in range(len(page_links)):
            # print(pages_threshold[threshold][i], page_links[i], page_titles[i], pages_updates[i])
            # print("******************")
            # print((page_links[i], page_titles[i], pages_threshold[threshold][i]))
            data.append((page_links[i], page_titles[i], pages_threshold[threshold][i]))
        # print("done collecting for threshold", threshold)
        if jsonFileName:
            with open("mainTopicsArticlesData" + str(threshold) + ".json", 'w') as f:
                json_string = json.dumps(data)
                f.write(json_string)
        datas[threshold] = data
    return datas

#reorganize the data to send it to the plot function
def plotMainArticlesUpdates(data=None, jsonFileName=None, id_=""):
    if jsonFileName:
        with open(jsonFileName) as json_file:
            data = json.load(json_file)
    titles = [x[1] for x in data]
    updates = [x[2] for x in data]
    plotUpdates(titles, updates, id_=id_)

#reorganize the data to send it to the plot function (this one is different because it plots data from two files)
def plotMainArticlesUpdates2(jsonFileName1, jsonFileName2, id_=""):
    with open(jsonFileName1) as json_file:
        data = json.load(json_file)
    titles = [x[1] for x in data]
    updates = [x[2] for x in data]
    with open(jsonFileName2) as json_file:
        data = json.load(json_file)
    updates2 = [x[2] for x in data]
    plotUpdates2(titles, updates, updates2, id_=id_)


if __name__ == "__main__":
    # t = [0, 210]
    # a = generateMainArticlesUpdateData(t, jsonFileName = "mainTopicsArticlesData1.json")
    # for i in t:
    #     json_file  ="tmp/mainTopicsArticlesData"+str(i)+".json"
    #     plotMainArticlesUpdates(jsonFileName = json_file, id_ = i)

    # plotMainArticlesUpdates2("tmp/mainTopicsArticlesData" + str(210) + ".json",
    #                      "tmp/mainTopicsArticlesData" + str(0) + ".json", id_='')
    pass
