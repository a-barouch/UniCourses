HISTORY_LIMIT_PER_QUERY = 1000
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import numpy as np
import time


def extractRandomPage():
    '''
    get a random article from wikipedia
    :return: a random article's name and url
    '''
    try:
      HEADERS = {'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                                'AppleWebKit/537.36 (KHTML, like Gecko)'
                                'Chrome/45.0.2454.101 Safari/537.36'),
                 'referer': 'http://stats.nba.com/scores/'}
      r = requests.get('https://en.wikipedia.org/wiki/Special:Random', headers=HEADERS)
    except requests.exceptions.Timeout as err:
        print("stuck")
        return None, None
    soup = BeautifulSoup(r.content, "html.parser")
    title = soup.find(id="firstHeading")
    return title.getText(), r.url


def old_compineDates(changes_times, bytes_for_change):
    if len(bytes_for_change) != len(changes_times):
        raise ("Error not the same length.")
    dates = {}
    min_d = min(changes_times) - timedelta(days=1)
    max_d = max(changes_times)
    while min_d <= max_d:
        min_d += timedelta(days=1)
        new_d = datetime(min_d.year, min_d.month, min_d.day)
        dates[new_d] = 0

    last_b = bytes_for_change[0]

    for d, b in zip(changes_times, bytes_for_change):
        new_d = datetime(d.year, d.month, d.day)
        if (abs(last_b - b) > 200):
            # print(abs(last_b -b) )
            # input()
            dates[new_d] += 1
        last_b = b
    return dates


def getDates(page_link):
    tmp = True
    changes_times = []
    bytes_for_change = []
    last_date = None
    while len(changes_times) < 10:
        history_link, params = generateHistoryLink(page_link, last_date)
        r = requests.get(history_link, params=params)
        soup = BeautifulSoup(r.content, 'html.parser')
        if tmp:
            with open("wikihis.html", 'w') as f:
                f.write(str(r.content))
            tmp = False
        dates_ofchanges_a_tags = soup.find_all("a", {"class": "mw-changeslist-date"})
        dates_ofchanges_span_tags = soup.find_all("span", {"class": "history-size mw-diff-bytes"})
        # print(len(dates_ofchanges_span_tags))
        # print(len(dates_ofchanges_a_tags))
        for a_tag, span_tag in zip(dates_ofchanges_a_tags, dates_ofchanges_span_tags):
            date_time_str = a_tag.text
            date_time_obj = datetime.strptime(date_time_str, '%H:%M, %d %B %Y')
            bytes_change = span_tag['data-mw-bytes']
            # if int(bytes_change) >100:
            changes_times.append(date_time_obj)
            bytes_for_change.append(int(bytes_change))
        last_date = date_time_obj
        # print(len(changes_times))
        # print(len(set(changes_times)))
    return changes_times, bytes_for_change


def generateHistoryLink(page_link: str, last_date: datetime = None):
    history_link = "https://en.wikipedia.org/w/index.php?title="
    title = re.search('\/([^\/]+)$', page_link).group(1)
    history_link += title + '&action=history'
    params = {'action': 'history'}
    params['title'] = title
    params['limit'] = HISTORY_LIMIT_PER_QUERY
    if last_date:
        params['offset'] = extractOffsetFromDate(last_date)
    else:
        params['offset'] = ''
    return history_link, params


def extractOffsetFromDate(offset_date: datetime):
    offset_str = offset_date.strftime("%Y%m%d%H%M%S")
    return offset_str


def count_updates():
    N = 100
    count = 0
    changes_list = []

    while True:
        try:
            # get a random wikipedia page
            _, main_page_link = extractRandomPage()
            if main_page_link == None:
                continue

            # count updates of article in the year 2021
            changes_times, bytes_for_change = getDates(main_page_link)
            dates_x = old_compineDates(changes_times, bytes_for_change)
            dates = list(dates_x.keys())
            changes = list(dates_x.values())
            changes = [changes[i] for i in range(len(dates)) if dates[i].year == 2021]
            val = sum(changes)

            # write to file
            with open("changes_DB.txt", "a") as file:
                file.write(str(val))
                file.write("\n")
            print(val)
            changes_list.append(val)
            count += 1

            if count == N:
                break
        except:
            continue



def plot_histogram():
    '''
    plot histogram of updates of random pages in the year 2021
    '''
    my_file = open("changes_DB.txt", "r")
    content = my_file.read()
    changes_list = content.split("\n")
    changes_list = [int(i) for i in changes_list]
    my_file.close()
    a = np.array(changes_list)
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.hist(a)
    plt.title("Edits per year histogram")
    plt.xlabel("Number of edits")
    plt.ylabel("Count")
    plt.savefig('updates_histogram.png')
    plt.show()


if __name__ == '__main__':
    count_updates()
    plot_histogram()
