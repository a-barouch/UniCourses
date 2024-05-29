import matplotlib.pyplot as plt
import seaborn as sns


# This file contains the functions of the plots

# this function plots titles on x axis and updates on y axis.
def plotUpdates(titles, updates, id_=""):
    sorted_idx = sorted(range(len(updates)), key=lambda k: updates[k])

    sorteded_titles = [titles[sorted_idx[i]] for i in range(len(titles))]
    sorteded_updates = [updates[sorted_idx[i]] for i in range(len(updates))]

    max_gab = 0
    for i in range(len(sorteded_updates) - 1):
        if sorteded_updates[i + 1] - sorteded_updates[i] > max_gab:
            max_gab = sorteded_updates[i + 1] - sorteded_updates[i]

    plt.plot(sorteded_titles, sorteded_updates)
    plt.ylabel('Number of updates in the last 5 years')
    plt.xlabel('Articles names')
    if id_ == 0:
        plt.title('Wikipedia\'s Main Articles sorted by number of updates')
    elif id_ == 210:
        plt.title('Wikipedia\'s Main Articles sorted by number of notable updates')
    else:
        raise ("find good name for plot")

    plt.xticks(rotation=90, size=9.5)
    plt.tight_layout()
    plt.savefig('pngs/plt_' + str(id_) + '.png', dpi=300)
    plt.show()


# this function plots titles on x axis and updates and updates2 on y axis.
def plotUpdates2(titles, updates, updates2, id_=""):
    sorted_idx = sorted(range(len(updates)), key=lambda k: updates[k])

    sorteded_titles = [titles[sorted_idx[i]] for i in range(len(titles))]
    sorteded_updates = [updates[sorted_idx[i]] for i in range(len(updates))]
    sorteded_updates2 = [updates2[sorted_idx[i]] for i in range(len(updates))]

    max_gab = 0
    for i in range(len(sorteded_updates) - 1):
        if sorteded_updates[i + 1] - sorteded_updates[i] > max_gab:
            max_gab = sorteded_updates[i + 1] - sorteded_updates[i]

    plt.plot(sorteded_titles, sorteded_updates, label='Filtered updates (threshold = 210 bytes)')
    plt.plot(sorteded_titles, sorteded_updates2, label='Non-filtered updates')
    plt.ylabel('Number of updates in the last 5 years')
    plt.xlabel('Articles names')
    if id_ == 0:
        plt.title('Wikipedia\'s Main Articles sorted by number of updates')
    elif id_ == 210:
        plt.title('Wikipedia\'s Main Articles sorted by number of notable updates')
    else:
        plt.title('Wikipedia\'s Main Articles sorted by number of updates')

    plt.legend()
    plt.xticks(rotation=90, size=9.5)
    plt.tight_layout()
    plt.savefig('pngs/combined.png', dpi=300)
    plt.show()


def plotTimes(times_dict):
    x, y = zip(*sorted(times_dict.items()))
    y = [abs(y_i) for y_i in y]
    a, b = [], []
    for p, q in zip(x, y):
        if q > 0:
            a.append(p)
            b.append(q)

    plt.plot(a, b)
    # plt.plot(sorteded_titles, sorteded_updates)
    # plt.ylabel('Number of updates in the last 5 years')
    # plt.xlabel('Articles names')
    # if id_ ==0:
    # plt.title('Wikipedia\'s Main Articles sorted by number of updates')
    # elif id_==210:
    # plt.title('Wikipedia\'s Main Articles sorted by number of notable updates')
    # else:
    # raise ("find good name for plot")

    plt.xticks(rotation=90, size=9.5)
    plt.tight_layout()
    plt.savefig('plt.png', dpi=300)
    # plt.show()
    plt.close()


# for plotting pages since their birth with the persentage of the updates
def plotTimesZeroOneDates(times_dict_arr, pngFiles, normalize=False):
    # subclass JSONEncoder
    # class DateTimeEncoder(JSONEncoder):
    #         #Override the default method
    #         def default(self, obj):
    #             if isinstance(obj, (datetime.date, datetime.datetime)):
    #                 return obj.isoformat()
    # employeeJSONData = json.dumps(times_dict_arr, indent=4, cls=DateTimeEncoder)
    # with open('collected_data/'+pngFiles[-1][:-4:]+"_json.json", 'w') as f:
    #     f.write(employeeJSONData)

    # to decode:
    # def DecodeDateTime(empDict):
    # if 'joindate' in empDict:
    #     empDict["joindate"] = dateutil.parser.parse(empDict["joindate"])
    #     return empDict
    # decodedJSON = json.loads(jsonData, object_hook=DecodeDateTime)

    all_dates = {}
    y_s, x_s = [], []
    k = {}
    for times_dict, pngf in zip(times_dict_arr, pngFiles):

        if not len(times_dict):
            x, y = [], []
        else:
            x, y = zip(*sorted(times_dict.items()))
        y = [abs(y_i) for y_i in y]
        if len(y) and sum(y):
            y = [y_i / sum(y) for y_i in y]

        a, b = [], []
        for p, q in zip(x, y):
            if q > 0:
                a.append(p)
                b.append(q)
        if len(a):
            minD = min(a)
            maxD = max(a)
        else:
            minD = 0
            maxD = 0
        if normalize:
            # if (maxD-minD):
            a = [(p - minD).total_seconds() / 3600 / 24 for p in a]
        # else:
        #     a = [(p - minD).total_seconds() for p in a]
        if len(a) < 20:
            continue
        # plt.plot(a,b, label = pngf[0:-4] )

        for a_i, b_i in zip(a, b):
            if a_i in all_dates:
                all_dates[a_i] += b_i
                k[a_i] += 1
            else:
                all_dates[a_i] = b_i
                k[a_i] = 1
        x_s += a
        y_s += b
        plt.plot(a, b, label=pngf[:-4], linewidth=2.0, alpha=0.4)

    for a_i in all_dates:
        all_dates[a_i] /= k[a_i]
    # x,y = zip(*sorted(all_dates.items()))
    sns.regplot(x_s, y_s, ci=None, fit_reg=True, color='black', scatter=False)

    # plt.plot(x,y, label = 'mean',linewidth=3.0,alpha=1, color = 'black' )

    # plt.plot(sorteded_titles, sorteded_updates)
    plt.ylabel('Persentage of update size')
    plt.xlabel('Days since page creation')
    # if id_ ==0:
    plt.title('Random pages lifespan')
    # elif id_==210:
    # plt.title('Wikipedia\'s Main Articles sorted by number of notable updates')
    # else:
    # raise ("find good name for plot")

    plt.xticks(rotation=90, size=9.5)
    # plt.legend(bbox_to_anchor=(1.05, 1.0, 0.5, 0.1), loc='best',prop={"size":2})
    # plt.figure(figsize=(20, 10))

    plt.tight_layout()
    plt.savefig(pngf, dpi=300)
    print(pngf)

    plt.close()
    # plt.show()


def plotTimesZeroOne(times_dict_arr, pngFiles):
    print(pngFiles[-1])
    for times_dict, pngf in zip(times_dict_arr, pngFiles):
        x, y = zip(*sorted(times_dict.items()))
        y = [abs(y_i) for y_i in y]
        if max(y):
            y = [y_i / max(y) for y_i in y]

        a, b = [], []
        for p, q in zip(x, y):
            if q > 0:
                a.append(p)
                b.append(q)
        minD = min(a)
        maxD = max(a)
        if (maxD - minD):
            a = [(p - minD).total_seconds() / (maxD - minD).total_seconds() for p in a]
        else:
            a = [(p - minD).total_seconds() for p in a]

        plt.plot(a, b, label=pngf[0:-10])
    # plt.plot(sorteded_titles, sorteded_updates)
    # plt.ylabel('Number of updates in the last 5 years')
    # plt.xlabel('Articles names')
    # if id_ ==0:
    # plt.title('Wikipedia\'s Main Articles sorted by number of updates')
    # elif id_==210:
    # plt.title('Wikipedia\'s Main Articles sorted by number of notable updates')
    # else:
    # raise ("find good name for plot")

    plt.xticks(rotation=90, size=9.5)
    plt.legend(loc='best', bbox_to_anchor=(0.5, 0.5, 0.1, 0.1), fontsize='xx-small', prop={"size": 2})
    # plt.figure(figsize=(20, 10))
    # plt.tight_layout()
    plt.savefig(pngf, dpi=300)
    print(pngf)
    plt.close()
    # plt.show()
