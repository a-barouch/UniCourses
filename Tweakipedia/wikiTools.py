import requests
from bs4 import BeautifulSoup
import wikipedia
import random

#get random page title and url
def extractRandomPage():
  r = requests.get('https://en.wikipedia.org/wiki/Special:Random')
  soup = BeautifulSoup(r.content, "html.parser")
  title  = soup.find(id="firstHeading")
  return title.getText(),r.url

#extract random neighbors of some page
def extractRandomConnectedPage(title, n=1):
  try:
    page_object = wikipedia.page(title,auto_suggest=False)
  except:
    return [], []
  n = min(n, len(page_object.links))
  random_linked = random.sample(page_object.links,  k=n)
  titles  = []
  urls  = []
  for rl in random_linked:
    try:
      page_object = wikipedia.page(rl, auto_suggest=False)
      titles.append(page_object.title)
      urls.append(page_object.url)
    except:
      continue
  return titles, urls

print(extractRandomPage())