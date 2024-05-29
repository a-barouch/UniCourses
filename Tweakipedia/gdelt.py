from gdeltdoc import GdeltDoc, Filters
from datetime import datetime, timedelta
import numpy as np
import re

# function that gets the needed info from gdelt
def gdeltdoc_usage(title,start_date, end_date):
    # print("in gdeltdoc_usage")
    # print(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    clean_title =re.sub("[^0-9a-zA-Z]+", " ", title)
    # print(clean_title)
    f = Filters(
        keyword=clean_title,
        start_date=start_date.strftime("%Y-%m-%d"),  # "2017-05-10",
        # country='IS',
        end_date=end_date.strftime("%Y-%m-%d")  # "2021-10-11"
    )
    gd = GdeltDoc()
    try :
        timeline = gd.timeline_search("timelinevol", f)

        dates = {}
        min_d = start_date - timedelta(days=1)

        while min_d <= end_date:
            min_d += timedelta(days=1)
            new_d = datetime(min_d.year, min_d.month, min_d.day)
            dates[new_d] = 0


        for j, i in timeline.iterrows():
            d = start_date + timedelta(days=j)
            new_d = datetime(i['datetime'].year, i['datetime'].month, i['datetime'].day)
            dates[new_d] += i['Volume Intensity']
            return np.average(np.array(list(dates.values())))
    except:
        return 0


# function that wraps the gdelt function
def gdeltMain(headers):
  now =datetime.now()
  today = datetime(now.year, now.month, now.day)
  last_month =  today - timedelta(days = 30)
  gdelt_vector = []
  for h in headers:
    gdelt_vector.append(gdeltdoc_usage(h, last_month, today))
  return gdelt_vector
