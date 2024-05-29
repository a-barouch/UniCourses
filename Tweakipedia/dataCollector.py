from datetime import datetime
from pageRank import pageRankMain
from updates import updatesRatioMain, updatesLastMonthMain, daysSinceLastUpdateMain,updatesLast5YearsMain
from gdelt import gdeltMain
from wikiTools import extractRandomPage, extractRandomConnectedPage
import wikipedia
import requests
import json
import pandas as pd
import numpy as np
import random
from featuresExtract import findCommunites, extractPageSize

#extracts the creation dates of the pages headers
def extractCreationDates_tmp(headers):
    pages = [wikipedia.page(name, auto_suggest=False) for name in headers]
    urls = ["https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvlimit=1&rvprop=timestamp&rvdir=newer&titles="+ page.title+"&format=json" for page in pages]
    times = []
    for i in range(len(urls)):
        try:
            r = requests.get(urls[i])
            d = json.loads(r.content)
            time = d['query']['pages'][str(pages[i].pageid)]['revisions'][0]['timestamp']
            time_lst = time.split("-")
            date = datetime(int(time_lst[0]), int(time_lst[1]), int(time_lst[2][:2]))
            times.append(date)
        except:
            date = datetime(2000, 1,1)
            times.append(date)

    return times
#extracts hours since creation dates of the pages headers
def extractCreationDates(headers):
    times = extractCreationDates_tmp(headers)
    hours_since_creation = []
    now = datetime.now()
    for t in times:
        hours_since_creation.append((now - t).total_seconds()/3600)
    return hours_since_creation

#extracts number of categories for pages headers
def extractNumOfCategories_tmp(headers):
    pages = [wikipedia.page(name, auto_suggest=False) for name in headers]
    cat_set = []
    for page in pages:
        cat_set = cat_set + page.categories
    cat_set = list(set(cat_set))
    total_vec = []
    for page in pages:
        cat_vec = [1 if cat_set[i] in page.categories else 0 for i in range(len(cat_set))]
        total_vec.append(cat_vec)
    return total_vec

#extracts number of categories for pages headers and rearrange them
def extractCategories(headers):
    total_vec = extractNumOfCategories_tmp(headers)
    return np.array(total_vec).T

#extracts number of references for pages headers
def extractNumOfRef(headers):
    pages = [wikipedia.page(name, auto_suggest=False) for name in headers]
    refs = []
    for page in pages:
        try:
            refs.append(len(page.references))
        except:
            refs.append(0)
    return refs

#extracts number of links out of every pages
def extractNumOfOutingPages(headers):
    pages = [wikipedia.page(name, auto_suggest=False) for name in headers]
    return [len(page.links) for page in pages]





def findCommunites_tmp( headers):
    try:
        return findCommunites( headers,0.1)
    except:
        return np.array([])
    # return [[1,0,0],[0,1,1]]

#extracts the communities of the pages by Girvan-Newman algorithm.
def extractCommunities(headers):
    coms = findCommunites_tmp(headers)
    return np.array(coms).T

#extracts the PageRank of the every pages (as if the pages are the only one in wikipedia)
def extractPageRank(page_mat, headers):
  return pageRankMain(page_mat, headers)
  return [0.3,0.1, 0.6]

#for every page extracts the ratio of the number of updates in the last month to the number of updates in the last year.
def extractNumberOfUpdatesRatio( headers):
  return updatesRatioMain(headers)
  return [0.1, 0.8, 0]

# for eevery page extracts the number of updates in the last month
def extractNumberOfUpdatesLastMonth( headers):
  return updatesLastMonthMain(headers)
  return [0.1, 0.8, 0]

# extracts number of days since last update for every page in headers
def extractSecondsSinceLastUpdate(headers):
  return daysSinceLastUpdateMain(headers)
  return [0.1, 0.8, 0]


# extracts GDELT value for every page in headers
def extractGdeltStat( headers):
  return gdeltMain(headers)
  return [0.1, 0.8, 0]

# build the adjacency matrix for the pages in headers
def buildAdjMat(headers, urls):
    number_of_pages  = len(headers)
    am = pd.DataFrame(np.zeros(shape=(number_of_pages, number_of_pages), dtype=int), columns=headers, index=headers)

    pages_links = {header : wikipedia.page(header, auto_suggest=False).links for header in headers}
    for header in headers:
        for linked in pages_links[header]:
            if linked in headers:
                am[header][linked] = 1
    am.to_csv("collected_dbs/"+str(random.randrange(9000)+1000) + "_links.csv", sep='\t')
    return am

#extracts m random pages and for every one n random pages of its neighbors
def extractRandomPages(m,n):
  headers = []
  urls = []
  for i in range(m):
    a, b = extractRandomPage()
    headers.append(a)
    urls.append(b)
    if n>0:
        x,y = extractRandomConnectedPage(a, n=n)
        for new_a, new_b in zip(x,y):
            if new_a not in headers:
                headers.append(new_a)
                urls.append(new_b)

  return headers, urls

def RunPageRankSmallExample():
    headers = ["University", "Israel", "Britney Spears", "Shakira", "Chimpanzee", "Gorilla", "Orangutan", "Potato", "Sweet potato", "Tomato", "Pop music", "Iran", "State of Palestine",  "Benjamin Netanyahu", "Madonna", "Science", "Beyonce", "Computer science",  "C++", "Europe"]

    df = pd.DataFrame(index=headers)
    print(df)

    adj_df = buildAdjMat(headers, [])

    # adding pageRank data to the data frame
    page_mat = adj_df.to_numpy()
    pagesRanks = extractPageRank(page_mat, headers)
    print(pagesRanks)
    return pagesRanks

#extracts random pages and their size and their number of updates to see of they are correlated.
def UpdatesVsSize(m):
    headers, urls = extractRandomPages(m, 0)
    df = pd.DataFrame(index=headers)
    adj_df = buildAdjMat(headers, urls)
    updates = updatesLast5YearsMain(headers)
    df['updatesLast5YearsMain'] = updates
    print("updatesLast5YearsMain done")
    updates = extractPageSize(headers)
    df['pageSize'] = updates
    print("pageSize done")
    df = df.copy()

    csv_file = "collected_dbs/updatesVsSize_" +"M"+str(m) +"_"+ str(random.randrange(9000) + 1000) + ".csv"
    print(csv_file)
    df.to_csv(csv_file, sep='\t')
    # print(df)
    return csv_file

# Builds the table for the learning
def buildDB(m, n):
  headers, urls = extractRandomPages(m,n)
  df = pd.DataFrame(index=headers)
  print(df)

  adj_df = buildAdjMat(headers, urls)

  #adding pageRank data to the data frame
  page_mat  = adj_df.to_numpy()
  pagesRanks = extractPageRank(page_mat, headers)
  df['pageRank'] = pagesRanks
  print("PageRank done")

  #adding UpdatesRatio data to the data frame
  updates = extractNumberOfUpdatesRatio(headers)
  df['updatesRatio'] = updates
  print("updatesRatio done")

  # adding Updates last month data to the data frame
  updates = extractNumberOfUpdatesLastMonth(headers)
  df['updatesLastMonth'] = updates
  print("updatesLastMonth done")

  # adding gdelt data to the data frame
  updates = extractGdeltStat(headers)
  df['gdeltStats'] = updates
  print("gdeltStats done")

  # adding creation date data to the data frame
  updates = extractCreationDates(headers)
  df['hoursSinceCreation'] = updates
  print("hoursSinceCreation done")

  # adding page size data to the data frame
  updates = extractPageSize(headers)
  df['pageSize'] = updates
  print("pageSize done")

  # adding categories to the data frame
  updates = extractCategories(headers)
  for i in range(len(updates)):
      if updates[i].sum() >1:
        df['category'+str(i)] = updates[i]
  print("categories done")

  # adding communities to the data frame
  updates = extractCommunities(headers)
  for i in range(len(updates)):
      if np.sum(updates[i]) > 1:
        df['community'+str(i)] = updates[i]
  print("Communities done")

  # adding references the data frame
  updates = extractNumOfRef(headers)
  df['numberOfReferences'] = updates
  print("numberOfReferences done")

  # adding references the data frame
  updates = extractNumOfOutingPages(headers)
  df['numberOfOutingPages'] = updates
  print("numberOfOutingPages done")

  # adding seconds since last update the data frame
  updates = extractSecondsSinceLastUpdate(headers)
  df['secondsSinceLastUpdate'] = updates
  print("secondsSinceLastUpdate done")
  # To get a de-fragmented frame
  df = df.copy()

  # csv_file = "collected_dbs/trainData" + str(random.randrange(9000) + 1000) + "_links.csv"
  csv_file = "collected_dbs/trainData_N" + str(n) +"M"+str(m) +"_"+ str(random.randrange(9000) + 1000) + "_links.csv"
  print(csv_file)
  df.to_csv(csv_file, sep='\t')
  # print(df)
  return csv_file

# RunPageRankSmallExample()
for i in range(10, 210, 10):
    for j in range(0, i+1, 5):
        csv_file = buildDB(i,j)
        print("done: m = "+str(i)+", n = "+str(j)+". Saved in file:"+csv_file)
# print(UpdatesVsSize(500))