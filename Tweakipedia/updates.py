import requests
from bs4 import BeautifulSoup
import re
import wikipedia
from datetime import datetime, date, timedelta
from urllib.parse import unquote

HISTORY_LIMIT_PER_QUERY = 1000
SUBJECT = "african elephant"


# This file contains all the scrapping of the updates from Wikipedia page
# static class that contains the functions that scrap data form some Wikipedia page
class WikiHelper:

    # convert datetime object to string
    def extractOffsetFromDate(offset_date: datetime):
        offset_str = offset_date.strftime("%Y%m%d%H%M%S")
        return offset_str

    # return the url that simulates the click on the edit history page for some article. last_date represents the
    # offset date meaning from which date to scrap the updates (the returned updates will be from before last_date)
    def generateHistoryLink(page_link: str, last_date: datetime = None):
        history_link = r"https://en.wikipedia.org/w/index.php?title="
        title = re.search('\/([^\/]+)$', page_link).group(1)
        history_link += title + '&action=history'
        params = {'action': 'history'}
        params['title'] = unquote(title)
        # params['token'] = unquote(title)

        params['limit'] = HISTORY_LIMIT_PER_QUERY
        if last_date:
            params['offset'] = WikiHelper.extractOffsetFromDate(last_date)
        else:
            params['offset'] = ''
        return history_link, params

    # given page_link and stop_at_date this function returns all the updates from stop_at_date to now. if
    # trim_after_before_stop_date is false the function may return more updates before stop_at_date. it returns two
    # arrays: filtered_times2 and changes_bytes2. filtered_times2 contains the dates and changes_bytes2 contains the
    # update size(in bytes) of the corresponding updates in the first array.
    def getDates(page_link, stop_at_date, trim_after_before_stop_date=True):
        changes_times = []
        bytes_for_change = []
        last_date = None
        noNew = True
        while (last_date is None or last_date > stop_at_date) and noNew:
            # while len(changes_times) < 10:
            history_link, params = WikiHelper.generateHistoryLink(
                page_link, last_date)
            # print(params)
            r = requests.get(history_link, params=params)
            soup = BeautifulSoup(r.content, 'html.parser')
            dates_ofchanges_a_tags = soup.find_all(
                "a", {"class": "mw-changeslist-date"})
            dates_ofchanges_span_tags = soup.find_all(
                "span", {"class": "history-size mw-diff-bytes"})
            if not len(dates_ofchanges_a_tags):
                noNew = False
                break
            # print(len(dates_ofchanges_span_tags))
            # print(len(dates_ofchanges_a_tags))
            for a_tag, span_tag in zip(dates_ofchanges_a_tags,
                                       dates_ofchanges_span_tags):
                date_time_str = a_tag.text
                # print(date_time_str)
                date_time_obj = datetime.strptime(date_time_str,
                                                  '%H:%M, %d %B %Y')
                bytes_change = span_tag['data-mw-bytes']
                # print(bytes_change)

                # if int(bytes_change) >100:
                changes_times.append(date_time_obj)
                bytes_for_change.append(int(bytes_change))
            last_date = date_time_obj

        if trim_after_before_stop_date:
            changes_times2 = []
            bytes_for_change2 = []

            for t, b in zip(changes_times, bytes_for_change):
                if t >= stop_at_date:
                    changes_times2.append(t)
                    bytes_for_change2.append(b)
            return changes_times2, bytes_for_change2
        return changes_times, bytes_for_change

    #combines two arrays one of dates and one of updates sizes in bytes and combine them in one dict
    def compineDates(changes_times, bytes_for_change, threshold = 200):
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
            if (abs(last_b - b) > threshold):
                dates[new_d] += abs(last_b - b)
            last_b = b

        return dates

    # filters the updates in two ways: first deletes the "undo" updates in which one undos what was done in another.
    # second it deletes negligible updates (identifying them by their size - smaller than the threshold).
    # mostly called after getDates function
    def cut_bytes(times, c_bytes, threshold=210):
        # print(times)
        # print(c_bytes)
        filtered_times = []
        changes_bytes = []
        for i in range(len(c_bytes) - 1):
            if abs(c_bytes[i + 1] - c_bytes[i]) >= threshold:
                changes_bytes.append(c_bytes[i] - c_bytes[i + 1])
                filtered_times.append(times[i])

        filtered_times2 = []
        changes_bytes2 = []
        i = 0
        while i < len(changes_bytes) - 1:
            if changes_bytes[i] + changes_bytes[i + 1]:
                changes_bytes2.append(changes_bytes[i])
                filtered_times2.append(filtered_times[i])
            else:
                i += 1
            i += 1
        return filtered_times2, changes_bytes2

    # given two arrays (the result of either cut_bytes or getDates) it deletes all the updates before stop_date and
    # returns the result
    def cut_bytes_to_date(times, c_bytes, stop_date):
        filtered_times = []
        changes_bytes = []
        for t, b in zip(times, c_bytes):
            if t >= stop_date:
                filtered_times.append(t)
                changes_bytes.append(b)

        return filtered_times, changes_bytes

    # for an array of updates and their size it sections the updates to periods of time. So we get array of dates and
    # for every date D the number of times there was an update in the period D - D+d.
    # d is the length of every period.
    # the function also returns a similar arrays explained above with a shift of d/2 in the dates
    def section_by_time(d: timedelta,
                        times,
                        changes,
                        start_date: datetime = None):
        sections = []
        sections_updates = []
        sections_halfs = []
        sections_updates_halfs = []
        today_t = date.today()
        if not len(times):
            return sections, sections_updates, sections_halfs, sections_updates_halfs
        if not start_date:
            print(times)
            start_date = min(times)
        end_date = datetime(today_t.year, today_t.month,
                            today_t.day) + timedelta(days=1)
        # print("starts:", start_date)
        while end_date > start_date - d:
            sections.append(end_date)
            sections_updates.append(0)
            sections_halfs.append(end_date - d / 2)
            sections_updates_halfs.append(0)
            end_date -= d
        for i in range(len(times)):
            update_date = times[i]
            for j in range(len(sections)):
                if j + 1 >= len(sections):
                    print("error: out of range, date: " + str(update_date))
                start_range = sections[j + 1]
                end_range = sections[j]
                if start_range <= update_date and update_date < end_range:
                    sections_updates[j] += 1
                    break
        for i in range(len(times)):
            update_date = times[i]
            for j in range(len(sections_halfs)):
                start_range = sections_halfs[j + 1]
                end_range = sections_halfs[j]
                if start_range <= update_date and update_date < end_range:
                    sections_updates_halfs[j] += 1
                    break

        return sections, sections_updates, sections_halfs, sections_updates_halfs

    #return the ratio of the updates in the last month to the updates u=in the last year.
    def getUpdateRatio(main_page_link):
        now = datetime.now()
        stop_date_year = datetime(now.year - 1, now.month, now.day)
        stop_date_month = datetime(now.year, now.month, now.day) - timedelta(days=30)
        changes_times, bytes_for_change = WikiHelper.getDates(main_page_link, stop_date_year)
        a_year, b_year = WikiHelper.cut_bytes(changes_times, bytes_for_change)
        a_month, b_month = WikiHelper.cut_bytes_to_date(a_year, b_year, stop_date_month)
        # print(a_year)
        if len(a_year):
            return len(a_month) / len(a_year)
        else:
            return 0

    # returns the number of updates  in the last month
    def getUpdatesLastMonth(main_page_link):
        now = datetime.now()
        stop_date_month = datetime(now.year, now.month, now.day) - timedelta(days=30)
        changes_times, bytes_for_change = WikiHelper.getDates(main_page_link, stop_date_month)
        a_month, b_month = WikiHelper.cut_bytes(changes_times, bytes_for_change)
        return len(a_month)

    #get the number of updates for certain page in the last 5 years
    def getUpdatesLast5Years(main_page_link):
        now = datetime.now()
        stop_date_month = datetime(now.year - 5, 1, 1)
        changes_times, bytes_for_change = WikiHelper.getDates(main_page_link, stop_date_month)
        a_month, b_month = WikiHelper.cut_bytes(changes_times, bytes_for_change, threshold=0)
        return len(a_month)

    # return number of days since last update
    def getDaysSinceLastUpdate(main_page_link):
        now = datetime.now()
        a_month, b_month = [], []
        days_gap = 100
        while len(a_month) == 0:
            print(main_page_link + " : " + str(days_gap))
            stop_date_month = datetime(now.year, now.month, now.day) - timedelta(days=days_gap)
            changes_times, bytes_for_change = WikiHelper.getDates(main_page_link, stop_date_month,
                                                                  trim_after_before_stop_date=False)
            a_month, b_month = WikiHelper.cut_bytes(changes_times, bytes_for_change)
            print(a_month)
            print(changes_times)
            if len(changes_times):
                days_gap = max(
                    (datetime(now.year, now.month, now.day) - min(changes_times)).total_seconds() / 3600 / 24,
                    days_gap + 100)
            else:
                days_gap = days_gap + 300

            if days_gap >= 1500 and not len(a_month):
                a_month = [datetime(now.year, now.month, now.day) - timedelta(days=days_gap)]
        return (now - max(a_month)).total_seconds()

    # gets two parameters: main_page_link that represent the page we want to scrap the updatesfore, since a datetime
    # object. return two arrays of the same length changes_times and bytes_for_change. changes_times contains the
    # dates of the updates and those go back to the date "since". and bytes_for_change contains the size of every
    # corresponding update in the array changes_times
    def getChangesUpdatesSince(main_page_link, since):
        changes_times, bytes_for_change = WikiHelper.getDates(main_page_link, since)
        return changes_times, bytes_for_change
    #not very successful one
    # def getUpdatesSince(main_page_link, since, thresholds = [50]):
    #     changes_times, bytes_for_change = WikiHelper.getDates(main_page_link, since)
    #     v= []
    #     for threshold in thresholds:
    #         a_month, b_month = WikiHelper.cut_bytes(changes_times, bytes_for_change, threshold = threshold)
    #         v.append(len(a_year))
    #     return v

# The parameter headers contains titles of pages in Wikipedia and this function returns array that in every
# corresponding index to the input array headers, will be the ratio of the page's updates in the last month to the
# last year
def updatesRatioMain(headers):
    print(headers)
    updates_vector = []
    for page_title in headers:
        page_object = wikipedia.page(page_title, auto_suggest=False)
        x = WikiHelper.getUpdateRatio(page_object.url)
        print(x)
        updates_vector.append(x)
    return updates_vector

# The parameter headers contains titles of pages in Wikipedia and the function returns array that in every
# corresponding index to the input array headers, will be the number of the page's updates in the last month
def updatesLastMonthMain(headers):
    updates_vector = []
    for page_title in headers:
        page_object = wikipedia.page(page_title, auto_suggest=False)
        updates_vector.append(WikiHelper.getUpdatesLastMonth(page_object.url))
    return updates_vector

# For every header in headers return the number of updates in the last 5 years in an array
def updatesLast5YearsMain(headers):
    updates_vector = []
    for page_title in headers:
        page_object = wikipedia.page(page_title, auto_suggest=False)
        updates_vector.append(WikiHelper.getUpdatesLast5Years(page_object.url))
    return updates_vector

# For every header in headers return the number of days since last update in an array
def daysSinceLastUpdateMain(headers):
    updates_vector = []
    for page_title in headers:
        page_object = wikipedia.page(page_title, auto_suggest=False)
        updates_vector.append(WikiHelper.getDaysSinceLastUpdate(page_object.url))
    return updates_vector


# For every page in the links array the function returns the dates of the updates since the peremeter "since" and the size of every update.
def updatesSinceMain(links, since):
    updates_vector_dates = []
    updates_vector_bytes = []
    for link in links:
        dates, changes = WikiHelper.getChangesUpdatesSince(link, since)
        updates_vector_dates.append(dates)
        updates_vector_bytes.append(changes)
        print("done: ", link, len(changes))
    return updates_vector_dates, updates_vector_bytes
