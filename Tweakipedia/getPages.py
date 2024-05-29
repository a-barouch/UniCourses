import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random

#this code file contains functions that extract pages connected to other pages

# root_link is a link to category page in wikipedia and this recursive function extracts all the pages in this
# category to some depth controled by the dive_to parameter
def getChildrenArticles(root_link, dive_to = 0,cats=[], save_in = 'pages.txt'):
    r = requests.get(root_link)
    soup = BeautifulSoup(r.content, "html.parser")
    root_title = soup.find(id="firstHeading").getText()
    cats.append((root_title, root_link))
    cat_divs = soup.find_all("div",class_="mw-category-group")
    with open(save_in, 'a') as f:
    # page_links = []
    # page_titles = []
        for cat_div in cat_divs:
            for a in cat_div.find_all("a"):
                if 'https://en.wikipedia.org/wiki/Category:' not in urljoin(r.url, a['href']):
                    f.write(urljoin(r.url, a['href']) + ","+a['title']+","+str(cats[2:3])+"\n")
    if dive_to ==0:
        return
    cat_divs = soup.find_all("div", {"class":"CategoryTreeSection"})
    page_links = []
    page_titles = []
    for cat_div in cat_divs:
        n = len(cat_div.find_all("a"))
        a = cat_div.find("a")
        getChildrenArticles(urljoin(r.url, a['href']),dive_to=  dive_to-1, save_in = save_in)


# returns all the Main_topic_classifications articles (not category)
def getRandomArticleInMainTopics():
    r = requests.get("https://en.wikipedia.org/wiki/Category:Main_topic_classifications")
    soup = BeautifulSoup(r.content, "html.parser")
    cat_divs = soup.find_all("div", {"class":"CategoryTreeSection"})

    page_links = []
    page_titles = []
    for cat_div in cat_divs:
        n = len(cat_div.find_all("a"))
        a = cat_div.find("a")
        page_links.append(urljoin(r.url, a['href']))
        page_titles.append(a.text)
    return page_links, page_titles

if __name__=="__main__":
    # getChildrenArticles("https://en.wikipedia.org/wiki/Category:Main_topic_classifications", dive_to=10,save_in = "pages6.txt")
    pass
    # print(getRandomArticleInMainTopics())