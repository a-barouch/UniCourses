
import pandas as pd
import numpy as np
from datetime import datetime
from updates import WikiHelper
import json 

#unused
def tmp():
    df = pd.read_csv('pagesCats.csv', sep='\t')
    df_part1 = df.loc[:387,:].drop('Category:other', axis=1)

    a = ['TITLE','Category:Academic discipline', 'Category:Business', 'Category:Communication', 'Category:Concept', 'Category:Culture', 'Category:Economy', 'Category:Education', 'Category:Energy', 'Category:Engineering', 'Category:Entertainment', 'Category:Non-physical entity', 'Category:Ethics', 'Category:Event (philosophy)', 'Category:Food and drink', 'Category:Geography', 'Category:Government', 'Category:Health', 'Category:History', 'Category:Human behavior', 'Category:Humanities', 'Category:Information', 'Category:Internet', 'Category:Knowledge', 'Category:Language', 'Category:Law', 'Category:Life', 'Category:Mass media', 'Category:Mathematics', 'Category:Military', 'Category:Music', 'Category:Nature', 'Category:Person', 'Category:Philosophy', 'Category:Politics', 'Category:Religion', 'Category:Science', 'Category:Society', 'Category:Sport', 'Category:Technology', 'Category:Time', 'Category:Universe','Category:other']
    b = ['TITLE','Category:other','Category:Academic discipline', 'Category:Business', 'Category:Communication', 'Category:Concept', 'Category:Culture', 'Category:Economy', 'Category:Education', 'Category:Energy', 'Category:Engineering', 'Category:Entertainment', 'Category:Non-physical entity', 'Category:Ethics', 'Category:Event (philosophy)', 'Category:Food and drink', 'Category:Geography', 'Category:Government', 'Category:Health', 'Category:History', 'Category:Human behavior', 'Category:Humanities', 'Category:Information', 'Category:Internet', 'Category:Knowledge', 'Category:Language', 'Category:Law', 'Category:Life', 'Category:Mass media', 'Category:Mathematics', 'Category:Military', 'Category:Music', 'Category:Nature', 'Category:Person', 'Category:Philosophy', 'Category:Politics', 'Category:Religion', 'Category:Science', 'Category:Society', 'Category:Sport', 'Category:Technology', 'Category:Time', 'Category:Universe']
    df_part2 = df.loc[388:,:].rename(columns = dict(zip(a, b))).drop('Category:other', axis=1)
    # print(df.loc[388:,:].rename(columns = dict(zip(a, b))).drop('Category:other', axis=1))

    
    frames = [df_part1, df_part2]
    # print(len(df_part1))
    # print(len(df_part2))
    # print(len(df_part1) + len(df_part2))
    pd.concat(frames).to_csv("RESULT.csv")
    result = pd.concat(frames).to_numpy()[:,1:].astype(int)
    headers = pd.concat(frames).to_numpy()[:,0]
    # print(result[0])
    # print(result)
    # print(len(result))
    # print(len(headers))

    MAIN_CATEGORIES = ['Category:Academic discipline', 'Category:Business', 'Category:Communication', 'Category:Concept', 'Category:Culture', 'Category:Economy', 'Category:Education', 'Category:Energy', 'Category:Engineering', 'Category:Entertainment', 'Category:Non-physical entity', 'Category:Ethics', 'Category:Event (philosophy)', 'Category:Food and drink', 'Category:Geography', 'Category:Government', 'Category:Health', 'Category:History', 'Category:Human behavior', 'Category:Humanities', 'Category:Information', 'Category:Internet', 'Category:Knowledge', 'Category:Language', 'Category:Law', 'Category:Life', 'Category:Mass media', 'Category:Mathematics', 'Category:Military', 'Category:Music', 'Category:Nature', 'Category:Person', 'Category:Philosophy', 'Category:Politics', 'Category:Religion', 'Category:Science', 'Category:Society', 'Category:Sport', 'Category:Technology', 'Category:Time', 'Category:Universe']
    pagesInCat = {}
    for i in MAIN_CATEGORIES:
        pagesInCat[i] = {}

    # print(len(result))
    for i in range(len(result)):
        a = result[i]
        # print(a)
        # print(a.sum())
        if a.sum():
            mindepth = np.min(a[np.nonzero(a)])
            cats_nums = np.where(a == mindepth)
            for c_n in cats_nums[0]:
                pagesInCat[MAIN_CATEGORIES[c_n]][headers[i]] = mindepth

    # print(pagesInCat)

# takes all the pages found in the big categories and find their updates data and save them for later use            
def readAllPagesCats(file_name):
    df = pd.read_csv(file_name, sep='\t', names = ['link', 'title', 'depth', 'category'])
    df = df.loc[41:,:].drop('depth', axis=1)
    headers = df.to_numpy()[:, 0]
    print(headers)
    data_dict = {}
    since_  = datetime.now()
    since_ = datetime(since_.year - 5, since_.month, 1)
    for h in headers:
        a1, b1, a2, b2 = WikiHelper.getUpdatesSince(h, since_)
        data_dict[h] = (a1, b1, a2, b2 )
        print('Done with: '+ h)
    with open('PagesCatsJson3.json', 'w') as f:
        f.write(json.dumps(data_dict, default=str))
readAllPagesCats('new_pages3.txt')