import requests
from updates import updatesSince
import wikipedia
from datetime import datetime
from plotData import plotTimesZeroOne,plotTimesZeroOneDates
from bs4 import BeautifulSoup
import json

#extract creation dates of the files in headers
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

#extract hours since creation dates of the files in headers
def extractCreationDates(headers):
    times = extractCreationDates_tmp(headers)
    hours_since_creation = []
    now = datetime.now()
    for t in times:
        hours_since_creation.append((now - t).total_seconds()/3600)
    return hours_since_creation

def updatesData(headers, times):
    create= extractCreationDates_tmp(headers)
    updates_vector, updates_vector2, byDay_b, byDay_c = updatesSince(headers, times)
    return updates_vector,updates_vector2, byDay_b, byDay_c

#extract random page
def getRandomArticle():
    
    r = requests.get('https://en.wikipedia.org/wiki/Special:Random')
    soup = BeautifulSoup(r.content, "html.parser")
    title  = soup.find(id="firstHeading")
    # page_object = wikipedia.page(title.getText(),auto_suggest=False)
    while len(r.content)< 100000:
        r = requests.get('https://en.wikipedia.org/wiki/Special:Random')
        soup = BeautifulSoup(r.content, "html.parser")
        title  = soup.find(id="firstHeading")

    return title.getText(),r.url

# ploting random pages to see their lifespan 
if __name__=='__main__':
    headers = []
    for i in range(50):
        headers.append(getRandomArticle()[0])

    #   = ['Bano Qudsia','Welfare capitalism', 'Three Arrows', 'Sumiyaa','Zippe','Wild Thing (film)','Psycho-Pass: The Movie', 'Law of averages', 'School uniform','Varsity letter']
    times = extractCreationDates_tmp(headers)

    updates_vector,updates_vector2, byDay_b, byDay_c = updatesData(headers, times)
    jsonData = {}
    for h,h_dict in zip(headers, byDay_c):
        jsonData[h]={}
        for daytmp in h_dict:
            jsonData[h][daytmp.strftime("%m/%d/%Y, %H:%M:%S")] = h_dict[daytmp]
        
    with open('collected_data/'+'_'.join(headers[-1].split(' '))+"__data.json",'w' ) as f:
        f.write(json.dumps(jsonData))
    # plotTimesZeroOneDates(byDay_b, pngFiles = ['_'.join(s.split(' '))+"_plot1.png" for s in headers])
    # plotTimesZeroOneDates(byDay_c, pngFiles = ['_'.join(s.split(' '))+"_.png" for s in headers])
    plotTimesZeroOneDates(byDay_c, pngFiles = ['graphs/'+'_'.join(s.split(' '))+"_normalized.png" for s in headers], normalize = True)