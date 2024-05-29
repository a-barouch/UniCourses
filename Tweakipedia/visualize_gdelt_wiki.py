import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, date, timedelta
import matplotlib.dates
import matplotlib.pyplot as plt
from gdeltdoc import GdeltDoc, Filters
import numpy as np
import scipy.stats
from pytrends.request import TrendReq
from pytrends import dailydata
import matplotlib.dates as mdates

HISTORY_LIMIT_PER_QUERY = 1000
MIN_BYTES = 200
SUBJECT = "Pfizer"
main_page_link = 'https://en.wikipedia.org/wiki/Pfizer'



def extractOffsetFromDate(offset_date: datetime):
    offset_str = offset_date.strftime("%Y%m%d%H%M%S")
    return offset_str


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


def gtrends(start_date, end_date):
    pytrend = TrendReq()
    kw_list = [SUBJECT]
    pytrend.build_payload(kw_list)
    start_year = start_date.year
    start_month = start_date.month
    end_year = end_date.year
    end_month = end_date.month
    df = dailydata.get_daily_data(SUBJECT, start_year, start_month, end_year, end_month, geo='')
    df = df.loc[start_date:end_date]
    df.index.name = 'date'
    df.reset_index(inplace=True)
    return df[SUBJECT]

def getDates(page_link):
    tmp = True
    changes_times = []
    bytes_for_change = []
    last_date = None
    while len(changes_times) < 10:
        history_link, params = generateHistoryLink(page_link, last_date)
        HEADERS = {'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                                  'AppleWebKit/537.36 (KHTML, like Gecko)'
                                  'Chrome/45.0.2454.101 Safari/537.36'),
                   'referer': 'http://stats.nba.com/scores/'}
        r = requests.get(history_link, params=params, headers = HEADERS)
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


def compineDates(changes_times, bytes_for_change):
    if len(bytes_for_change) != len(changes_times):
        raise ("Error not the same length.")
    dates = {}
    min_d = min(changes_times) - timedelta(days=1)
    print(min_d)
    max_d = max(changes_times)
    print(max_d)
    while min_d <= max_d:
        min_d += timedelta(days=1)
        new_d = datetime(min_d.year, min_d.month, min_d.day)
        dates[new_d] = 0

    last_b = bytes_for_change[0]
    for d, b in zip(changes_times, bytes_for_change):
        new_d = datetime(d.year, d.month, d.day)
        if (abs(last_b - b) > MIN_BYTES):
            dates[new_d] += abs(last_b - b)
            # print("&&&&&&&&&&&&&&&&&",b, abs(last_b -b))
            # print(abs(last_b -b))
        last_b = b

    return dates


def old_compineDates(changes_times, bytes_for_change):
    if len(bytes_for_change) != len(changes_times):
        raise ("Error not the same length.")
    dates = {}
    min_d = min(changes_times) - timedelta(days=1)
    # print(min_d)
    max_d = max(changes_times)
    # print(max_d)
    while min_d <= max_d:
        min_d += timedelta(days=1)
        new_d = datetime(min_d.year, min_d.month, min_d.day)
        dates[new_d] = 0

    last_b = bytes_for_change[0]

    for d, b in zip(changes_times, bytes_for_change):
        new_d = datetime(d.year, d.month, d.day)
        if (abs(last_b - b) > MIN_BYTES):
            # print(abs(last_b -b) )
            # input()
            dates[new_d] += 1
        last_b = b

    return dates


def gdeltdoc_usage(start_date, end_date):
    # print("^^^^^^^^^^^^^", start_date, end_date)
    print("in gdeltdoc_usage")
    print(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    f = Filters(
        keyword=SUBJECT,
        start_date=start_date.strftime("%Y-%m-%d"),  # "2017-05-10",
        # country='IS',
        end_date=end_date.strftime("%Y-%m-%d")  # "2021-10-11"
    )
    gd = GdeltDoc()
    timeline = gd.timeline_search("timelinevol", f)
    print(timeline)

    dates = {}
    min_d = start_date - timedelta(days=1)
    # min_d = start_date -timedelta(days=1)
    print("*44444444", min_d, end_date)
    # r = True
    while min_d <= end_date:
        min_d += timedelta(days=1)
        new_d = datetime(min_d.year, min_d.month, min_d.day)
        # if r :
        # print(new_d)
        # r=False
        dates[new_d] = 0

    # Search for articles matching the filters
    # articles = gd.article_search(f)
    # Get a timeline of the number of articles matching the filters
    # articles = gd.article_search(f)

    for j, i in timeline.iterrows():
        d = start_date + timedelta(days=j)
        # print("date ", d )
        # print("i ", i['Volume Intensity'] )
        new_d = datetime(i['datetime'].year, i['datetime'].month, i['datetime'].day)
        # print()
        dates[new_d] += i['Volume Intensity']
    # print("dates of gdelt and the data as dict:")
    # print(dates)

    # plt.plot(timeline["Volume Intensity"])
    # plt.show()
    # b=timeline.iloc[:,1].values
    # print(list(dates.keys()))
    return np.array(list(dates.values()))


def running_meanFast(x, N):
    return np.convolve(x, np.ones((N,))/N)[(N-1):]

def plot_data(t, data1, data2, data3):
    if len(t) != len(data1) or len(data1) != len(data2):
        raise ("Sizes Error")
    X = 15 # smoothing variable

    # smooth data
    data1 = running_meanFast(data1, X)
    data2 = running_meanFast(data2, X)
    data3 = running_meanFast(data3, X)

    # compute correlation between wikipedia edits to gdelt and gtrends
    corr1,p1 = scipy.stats.pearsonr(data1, data2)
    corr2, p2 = scipy.stats.pearsonr(data1, data3)
    print("Gdelt Correlation = "+str(corr1)+", p value = "+str(p1))
    print("Google trends Correlation = " + str(corr2) + ", p value = " + str(p2))

    # specify x axis ticks date format
    locator = mdates.MonthLocator()  # every month
    fmt = mdates.DateFormatter('%b %y')

    # plot wikipedia edits
    fig, ax1 = plt.subplots()
    color = 'tab:red'
    ax1.set_xlabel('time (months)')
    ax1.set_ylabel('number of changes', color=color)
    ax1.plot(t, data1, color=color, alpha = 0.5)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xticklabels(t, rotation=90)
    ax1.title.set_text(SUBJECT + ": Gdelt, Google trends and Wikipedia trends comparison")

    ax2 = ax1.twinx()
    ax3 = ax1.twinx()
    ax2.spines["right"].set_position(("axes", 1.2))
    ax3.spines["right"].set_position(("axes", 1))

    # plot gdelt
    color = 'tab:blue'
    ax2.set_ylabel('gdelt: media percentage', color=color)
    ax2.plot(t, data2, color=color, alpha=0.3)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.yaxis.set_label_position('right')
    ax2.yaxis.set_ticks_position('right')
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    X = plt.gca().xaxis
    X.set_major_locator(locator)
    X.set_major_formatter(fmt)

    # plot google trends
    color = 'tab:green'
    ax3.set_ylabel('google trends: search percentage', color=color)  # we already handled the x-label with ax1
    ax3.plot(t, data3, color=color, alpha=0.3)
    ax3.tick_params(axis='y', labelcolor=color)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    # X = plt.gca().xaxis
    ax3.yaxis.set_label_position('right')
    ax3.yaxis.set_ticks_position('right')
    # X.set_major_locator(locator)
    # # Specify formatter
    # X.set_major_formatter(fmt)

    plt.savefig(SUBJECT+'.png')
    plt.show()


if __name__ == '__main__':
    # read in wikipedia updates from selected article
    changes_times, bytes_for_change = getDates(main_page_link)
    dates_x = old_compineDates(changes_times, bytes_for_change)
    x_values = list(dates_x.keys())
    y_values = list(dates_x.values())
    changes_per_day = np.array(y_values)
    min_d = min(x_values)
    max_d = max(x_values)
    dates = matplotlib.dates.date2num(x_values)
    dates_x = compineDates(changes_times, bytes_for_change)
    x_values = list(dates_x.keys())
    y_values = list(dates_x.values())

    # get google trend data that corresponds to the dates from wikipedia
    gtrends_data = gtrends(min_d, max_d)
    gtrends_data = gtrends_data.to_numpy()

    # get gdelt data that corresponds to the dates from wikipedia
    gdelt_data = gdeltdoc_usage(min_d, max_d)
    chars_change = np.array(y_values)
    dates_from_x_values = x_values

    # fix arrays
    if len(gdelt_data) == len(x_values) + 1:
        gdelt_data = gdelt_data[:-1]
    diff =  len(changes_per_day) - len(gtrends_data)
    if diff > 0:
        changes_per_day = changes_per_day[:-diff]
        dates_from_x_values = dates_from_x_values[:-diff]
        gdelt_data = gdelt_data[:-diff]

    # plot
    plot_data(dates_from_x_values, changes_per_day, gdelt_data,gtrends_data)
