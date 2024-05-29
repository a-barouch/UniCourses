import visualize_gdelt_wiki as vis
import wikipedia
import numpy as np
import matplotlib.dates
import matplotlib.pyplot as plt
import re
from datetime import datetime


def plot_data(t, data, death_date, title):
    import matplotlib.dates as mdates
    if len(t) != len(data):
        raise ("Sizes Error")

    # Set the locator
    locator = mdates.MonthLocator()  # every month
    # Specify the format - %b gives us Jan, Feb...
    fmt = mdates.DateFormatter('%b %y')

    color = 'tab:pink'
    plt.xlabel('time (months)')
    plt.ylabel('number of edits in article')

    # add date of demise
    plt.axvline(x=death_date, color='c', linewidth=3, alpha=0.5)
    plt.text(death_date, plt.axis()[3] / 2, "death", rotation=90, verticalalignment='center')

    # plot edits to wikipedia article
    plt.plot(t, data, color=color)
    plt.tick_params(axis='y')
    plt.xticks(rotation=90)
    plt.title(title + " updates in relation to date of demise")
    X = plt.gca().xaxis
    X.set_major_locator(locator)
    X.set_major_formatter(fmt)

    plt.savefig(title + "_death.png")
    plt.show()


def stats():
    my_file = open("time_to_update_death.txt", "r")
    content = my_file.read()
    days = content.split("\n")
    days = [int(i) for i in days]
    print(np.mean(days))
    print(np.std(days))


# read in a list of people extracted from wikipedia by their category
my_file = open("2018_deaths.txt", "r", encoding='utf-8')
content = my_file.read()
pages_list = content.split("\n")
pages_list = [x for x in pages_list if not x.startswith('to del:')]

# regex to detect a pattern of the form: '14 January 2016)' to read the date of demise
regex = '(([0-9])|([0-2][0-9])|([3][0-1]))\s(January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}\)'
index = 0  # change index if part of the list was read
min_year = 2017  # year from which to look for exits in the page (should be before death)
pages_list = pages_list[index:]
for name in pages_list:
    try:
        page_object = wikipedia.page(name, auto_suggest=False)
        summary = page_object.summary
        url = page_object.url
        res = re.search(regex, summary)
        # if the date of demise exists in the exact format in the summary
        # (some pages do not include an exact date and we ignore them)
        if res:
            # read date to a datetime format
            death_date = datetime.strptime(res.group()[:-1], '%d %B %Y')

            # extract edits data of the article
            changes_times, bytes_for_change = vis.getDates(url)
            dates_x = vis.old_compineDates(changes_times, bytes_for_change)
            dates = list(dates_x.keys())
            changes = list(dates_x.values())
            changes = [changes[i] for i in range(len(dates)) if dates[i].year > min_year]
            dates = [dates[i] for i in range(len(dates)) if dates[i].year > min_year]
            if (death_date - dates[0]).days < 0:  # page created after the death of the person
                continue

            changes_per_day = np.array(changes)
            dates_num = matplotlib.dates.date2num(dates)

            # plot to edits in relation to a person's death
            plot_data(dates_num, changes_per_day, death_date, page_object.title)

            # get a list of dates with updates to the article
            dates_with_changes = [dates[i] for i in range(len(dates)) if changes[i] > 0]

            # find closest edit to the person's death after the death
            dist = [(dates_with_changes[i] - death_date).days for i in range(len(dates_with_changes))]
            dist = [i for i in dist if i >= 0]
            with open("time_to_update_death.txt", "a", encoding='utf-8') as f:
                f.write(str(min(dist)))
                f.write(("\n"))
            index += 1
            print(index)

    except UnboundLocalError:
        continue
