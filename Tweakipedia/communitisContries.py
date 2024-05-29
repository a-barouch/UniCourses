from datetime import timedelta, datetime, date

import fontTools.afmLib
from numpy import dot
import numpy as np
from numpy.linalg import norm

import requests
import wikipedia
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from updates import WikiHelper
from featuresExtract import findCommunites

#given headers constract the dataframe of the adjacency matrix accourding to the cosine similarity on the updates vector of the last 10 years
def findSimByUpdates(headers, urls, data2= None,  data2_av = False, threshold = 0.5):
    headers_data = {}
    today = date.today()
    ten_years_ago = datetime(today.year-10, 1, 1)
    if not data2_av:
        for h,u in zip(headers, urls):
            a1,b1,a2,b2 = WikiHelper.getUpdatesSince(u, ten_years_ago)
            headers_data[h] = a2
        print(headers_data)
    data = np.zeros((len(headers), len(headers)), dtype=int)
    if not data2_av:
        data2 = np.zeros((len(headers), len(headers)), dtype=np.float)
    # print(headers_data['Ecuador'])
    for i in range(len(headers)):
        for j in range(i+1, len(headers)):
            # print(headers[i], headers[j])
            if not data2_av:
                sections_i, sections_updates_i, sections_halfs_i, sections_updates_halfs_i = WikiHelper.section_by_time(timedelta(days=7), headers_data[headers[i]],[], start_date=ten_years_ago)
                sections_j, sections_updates_j, sections_halfs_j, sections_updates_halfs_j = WikiHelper.section_by_time(timedelta(days=7), headers_data[headers[j]],[], start_date=ten_years_ago)
                if len(sections_updates_j) == 0:
                    print(headers[j])
                if len(sections_updates_i) == 0:
                    print(headers[i])

                cos_sim_1 = dot(sections_updates_i, sections_updates_j)/(norm(sections_updates_i)*norm(sections_updates_j))
                cos_sim_2 = dot(sections_updates_halfs_i, sections_updates_halfs_j)/(norm(sections_updates_halfs_i)*norm(sections_updates_halfs_j))
            # print(sections_updates_i)
            print(headers[i], headers[j])
            # data[i][j] = data[j][i] = (cos_sim_1+cos_sim_2)/2
            if not data2_av:
                data2[i][j] = data2[j][i] = max(cos_sim_1, cos_sim_2)
            data[i][j] = data[j][i] = int(data2[j][i] >=threshold)
            print(data2[j][i])

            # input()
    print(data)
    print(data.mean())
    print(data2.mean())
    if not data2_av:
        df = pd.DataFrame(data2, columns=headers, index=headers)
        df.to_csv('SimilarComtriesByUpdatesCosine.csv')
    df = pd.DataFrame(data, columns=headers, index=headers)
    df.to_csv('SimilarComtriesByUpdates'+str(threshold)+'.csv')
    coms = findCommunites(headers, 0.1, df_np=data)
    # with open('communitiesResult.txt', 'w') as f:
    # # f.write(str(coms))
    with open('communitiesResult'+str(threshold)+'.txt', 'w') as f:
        f.write(str(coms))
    # df = pd.DataFrame(coms, columns=headers, index=headers)
    # df.to_csv('SimilarComtriesByUpdatesCommunities.csv')

#extract all the countries and their webpages in wikipedia (some of them are done manually since wikipedia redirect them)
def extractContriesHeaders():
    # countries ={'Afghanistan': 'AF', 'Albania': 'AL', 'Algeria': 'DZ', 'American Samoa': 'AS', 'AndorrA': 'AD', 'Angola': 'AO', 'Anguilla': 'AI', 'Antarctica': 'AQ', 'Antigua and Barbuda': 'AG', 'Argentina': 'AR', 'Armenia': 'AM', 'Aruba': 'AW', 'Australia': 'AU', 'Austria': 'AT', 'Azerbaijan': 'AZ', 'Bahamas': 'BS', 'Bahrain': 'BH', 'Bangladesh': 'BD', 'Barbados': 'BB', 'Belarus': 'BY', 'Belgium': 'BE', 'Belize': 'BZ', 'Benin': 'BJ', 'Bermuda': 'BM', 'Bhutan': 'BT', 'Bolivia': 'BO', 'Bosnia and Herzegovina': 'BA', 'Botswana': 'BW', 'Bouvet Island': 'BV', 'Brazil': 'BR', 'British Indian Ocean Territory': 'IO', 'Brunei Darussalam': 'BN', 'Bulgaria': 'BG', 'Burkina Faso': 'BF', 'Burundi': 'BI', 'Cambodia': 'KH', 'Cameroon': 'CM', 'Canada': 'CA', 'Cape Verde': 'CV', 'Cayman Islands': 'KY', 'Central African Republic': 'CF', 'Chad': 'TD', 'Chile': 'CL', 'China': 'CN', 'Christmas Island': 'CX', 'Cocos (Keeling) Islands': 'CC', 'Colombia': 'CO', 'Comoros': 'KM', 'Congo': 'CG', 'Congo, The Democratic Republic of the': 'CD', 'Cook Islands': 'CK', 'Costa Rica': 'CR', 'Cote D"Ivoire': 'CI', 'Croatia': 'HR', 'Cuba': 'CU', 'Cyprus': 'CY', 'Czech Republic': 'CZ', 'Denmark': 'DK', 'Djibouti': 'DJ', 'Dominica': 'DM', 'Dominican Republic': 'DO', 'Ecuador': 'EC', 'Egypt': 'EG', 'El Salvador': 'SV', 'Equatorial Guinea': 'GQ', 'Eritrea': 'ER', 'Estonia': 'EE', 'Ethiopia': 'ET', 'Falkland Islands (Malvinas)': 'FK', 'Faroe Islands': 'FO', 'Fiji': 'FJ', 'Finland': 'FI', 'France': 'FR', 'French Guiana': 'GF', 'French Polynesia': 'PF', 'French Southern Territories': 'TF', 'Gabon': 'GA', 'Gambia': 'GM', 'Georgia': 'GE', 'Germany': 'DE', 'Ghana': 'GH', 'Gibraltar': 'GI', 'Greece': 'GR', 'Greenland': 'GL', 'Grenada': 'GD', 'Guadeloupe': 'GP', 'Guam': 'GU', 'Guatemala': 'GT', 'Guernsey': 'GG', 'Guinea': 'GN', 'Guinea-Bissau': 'GW', 'Guyana': 'GY', 'Haiti': 'HT', 'Heard Island and Mcdonald Islands': 'HM', 'Holy See (Vatican City State)': 'VA', 'Honduras': 'HN', 'Hong Kong': 'HK', 'Hungary': 'HU', 'Iceland': 'IS', 'India': 'IN', 'Indonesia': 'ID', 'Iran, Islamic Republic Of': 'IR', 'Iraq': 'IQ', 'Ireland': 'IE', 'Isle of Man': 'IM', 'Israel': 'IL', 'Italy': 'IT', 'Jamaica': 'JM', 'Japan': 'JP', 'Jersey': 'JE', 'Jordan': 'JO', 'Kazakhstan': 'KZ', 'Kenya': 'KE', 'Kiribati': 'KI', 'Korea, Democratic People"S Republic of': 'KP', 'Korea, Republic of': 'KR', 'Kuwait': 'KW', 'Kyrgyzstan': 'KG', 'Lao People"S Democratic Republic': 'LA', 'Latvia': 'LV', 'Lebanon': 'LB', 'Lesotho': 'LS', 'Liberia': 'LR', 'Libyan Arab Jamahiriya': 'LY', 'Liechtenstein': 'LI', 'Lithuania': 'LT', 'Luxembourg': 'LU', 'Macao': 'MO', 'Macedonia, The Former Yugoslav Republic of': 'MK', 'Madagascar': 'MG', 'Malawi': 'MW', 'Malaysia': 'MY', 'Maldives': 'MV', 'Mali': 'ML', 'Malta': 'MT', 'Marshall Islands': 'MH', 'Martinique': 'MQ', 'Mauritania': 'MR', 'Mauritius': 'MU', 'Mayotte': 'YT', 'Mexico': 'MX', 'Micronesia, Federated States of': 'FM', 'Moldova, Republic of': 'MD', 'Monaco': 'MC', 'Mongolia': 'MN', 'Montenegro': 'ME', 'Montserrat': 'MS', 'Morocco': 'MA', 'Mozambique': 'MZ', 'Myanmar': 'MM', 'Namibia': 'NA', 'Nauru': 'NR', 'Nepal': 'NP', 'Netherlands': 'NL', 'Netherlands Antilles': 'AN', 'New Caledonia': 'NC', 'New Zealand': 'NZ', 'Nicaragua': 'NI', 'Niger': 'NE', 'Nigeria': 'NG', 'Niue': 'NU', 'Norfolk Island': 'NF', 'Northern Mariana Islands': 'MP', 'Norway': 'NO', 'Oman': 'OM', 'Pakistan': 'PK', 'Palau': 'PW', 'Palestinian Territory, Occupied': 'PS', 'Panama': 'PA', 'Papua New Guinea': 'PG', 'Paraguay': 'PY', 'Peru': 'PE', 'Philippines': 'PH', 'Pitcairn': 'PN', 'Poland': 'PL', 'Portugal': 'PT', 'Puerto Rico': 'PR', 'Qatar': 'QA', 'Reunion': 'RE', 'Romania': 'RO', 'Russian Federation': 'RU', 'RWANDA': 'RW', 'Saint Helena': 'SH', 'Saint Kitts and Nevis': 'KN', 'Saint Lucia': 'LC', 'Saint Pierre and Miquelon': 'PM', 'Saint Vincent and the Grenadines': 'VC', 'Samoa': 'WS', 'San Marino': 'SM', 'Sao Tome and Principe': 'ST', 'Saudi Arabia': 'SA', 'Senegal': 'SN', 'Serbia': 'RS', 'Seychelles': 'SC', 'Sierra Leone': 'SL', 'Singapore': 'SG', 'Slovakia': 'SK', 'Slovenia': 'SI', 'Solomon Islands': 'SB', 'Somalia': 'SO', 'South Africa': 'ZA', 'South Georgia and the South Sandwich Islands': 'GS', 'Spain': 'ES', 'Sri Lanka': 'LK', 'Sudan': 'SD', 'Suriname': 'SR', 'Svalbard and Jan Mayen': 'SJ', 'Swaziland': 'SZ', 'Sweden': 'SE', 'Switzerland': 'CH', 'Syrian Arab Republic': 'SY', 'Taiwan, Province of China': 'TW', 'Tajikistan': 'TJ', 'Tanzania, United Republic of': 'TZ', 'Thailand': 'TH', 'Timor-Leste': 'TL', 'Togo': 'TG', 'Tokelau': 'TK', 'Tonga': 'TO', 'Trinidad and Tobago': 'TT', 'Tunisia': 'TN', 'Turkey': 'TR', 'Turkmenistan': 'TM', 'Turks and Caicos Islands': 'TC', 'Tuvalu': 'TV', 'Uganda': 'UG', 'Ukraine': 'UA', 'United Arab Emirates': 'AE', 'United Kingdom': 'GB', 'United States': 'US', 'United States Minor Outlying Islands': 'UM', 'Uruguay': 'UY', 'Uzbekistan': 'UZ', 'Vanuatu': 'VU', 'Venezuela': 'VE', 'Viet Nam': 'VN', 'Virgin Islands, British': 'VG', 'Virgin Islands, U.S.': 'VI', 'Wallis and Futuna': 'WF', 'Western Sahara': 'EH', 'Yemen': 'YE', 'Zambia': 'ZM', 'Zimbabwe': 'ZW'}
    # countries ={"AF":"Afghanistan","AX":"\u00c5land Islands","AL":"Albania","DZ":"Algeria","AS":"American Samoa","AD":"Andorra","AO":"Angola","AI":"Anguilla","AQ":"Antarctica","AG":"Antigua & Barbuda","AR":"Argentina","AM":"Armenia","AW":"Aruba","AU":"Australia","AT":"Austria","AZ":"Azerbaijan","BS":"Bahamas","BH":"Bahrain","BD":"Bangladesh","BB":"Barbados","BY":"Belarus","BE":"Belgium","BZ":"Belize","BJ":"Benin","BM":"Bermuda","BT":"Bhutan","BO":"Bolivia","BA":"Bosnia & Herzegovina","BW":"Botswana","BV":"Bouvet Island","BR":"Brazil","IO":"British Indian Ocean Territory","VG":"British Virgin Islands","BN":"Brunei","BG":"Bulgaria","BF":"Burkina Faso","BI":"Burundi","KH":"Cambodia","CM":"Cameroon","CA":"Canada","CV":"Cape Verde","BQ":"Caribbean Netherlands","KY":"Cayman Islands","CF":"Central African Republic","TD":"Chad","CL":"Chile","CN":"China","CX":"Christmas Island","CC":"Cocos (Keeling) Islands","CO":"Colombia","KM":"Comoros","CG":"Congo - Brazzaville","CD":"Congo - Kinshasa","CK":"Cook Islands","CR":"Costa Rica","CI":"C\u00f4te d\u2019Ivoire","HR":"Croatia","CU":"Cuba","CW":"Cura\u00e7ao","CY":"Cyprus","CZ":"Czechia","DK":"Denmark","DJ":"Djibouti","DM":"Dominica","DO":"Dominican Republic","EC":"Ecuador","EG":"Egypt","SV":"El Salvador","GQ":"Equatorial Guinea","ER":"Eritrea","EE":"Estonia","SZ":"Eswatini","ET":"Ethiopia","FK":"Falkland Islands","FO":"Faroe Islands","FJ":"Fiji","FI":"Finland","FR":"France","GF":"French Guiana","PF":"French Polynesia","TF":"French Southern Territories","GA":"Gabon","GM":"Gambia","GE":"Georgia","DE":"Germany","GH":"Ghana","GI":"Gibraltar","GR":"Greece","GL":"Greenland","GD":"Grenada","GP":"Guadeloupe","GU":"Guam","GT":"Guatemala","GG":"Guernsey","GN":"Guinea","GW":"Guinea-Bissau","GY":"Guyana","HT":"Haiti","HM":"Heard & McDonald Islands","HN":"Honduras","HK":"Hong Kong SAR China","HU":"Hungary","IS":"Iceland","IN":"India","ID":"Indonesia","IR":"Iran","IQ":"Iraq","IE":"Ireland","IM":"Isle of Man","IL":"Israel","IT":"Italy","JM":"Jamaica","JP":"Japan","JE":"Jersey","JO":"Jordan","KZ":"Kazakhstan","KE":"Kenya","KI":"Kiribati","KW":"Kuwait","KG":"Kyrgyzstan","LA":"Laos","LV":"Latvia","LB":"Lebanon","LS":"Lesotho","LR":"Liberia","LY":"Libya","LI":"Liechtenstein","LT":"Lithuania","LU":"Luxembourg","MO":"Macao SAR China","MG":"Madagascar","MW":"Malawi","MY":"Malaysia","MV":"Maldives","ML":"Mali","MT":"Malta","MH":"Marshall Islands","MQ":"Martinique","MR":"Mauritania","MU":"Mauritius","YT":"Mayotte","MX":"Mexico","FM":"Micronesia","MD":"Moldova","MC":"Monaco","MN":"Mongolia","ME":"Montenegro","MS":"Montserrat","MA":"Morocco","MZ":"Mozambique","MM":"Myanmar (Burma)","NA":"Namibia","NR":"Nauru","NP":"Nepal","NL":"Netherlands","NC":"New Caledonia","NZ":"New Zealand","NI":"Nicaragua","NE":"Niger","NG":"Nigeria","NU":"Niue","NF":"Norfolk Island","KP":"North Korea","MK":"North Macedonia","MP":"Northern Mariana Islands","NO":"Norway","OM":"Oman","PK":"Pakistan","PW":"Palau","PS":"Palestinian Territories","PA":"Panama","PG":"Papua New Guinea","PY":"Paraguay","PE":"Peru","PH":"Philippines","PN":"Pitcairn Islands","PL":"Poland","PT":"Portugal","PR":"Puerto Rico","QA":"Qatar","RE":"R\u00e9union","RO":"Romania","RU":"Russia","RW":"Rwanda","WS":"Samoa","SM":"San Marino","ST":"S\u00e3o Tom\u00e9 & Pr\u00edncipe","SA":"Saudi Arabia","SN":"Senegal","RS":"Serbia","SC":"Seychelles","SL":"Sierra Leone","SG":"Singapore","SX":"Sint Maarten","SK":"Slovakia","SI":"Slovenia","SB":"Solomon Islands","SO":"Somalia","ZA":"South Africa","GS":"South Georgia & South Sandwich Islands","KR":"South Korea","SS":"South Sudan","ES":"Spain","LK":"Sri Lanka","BL":"St. Barth\u00e9lemy","SH":"St. Helena","KN":"St. Kitts & Nevis","LC":"St. Lucia","MF":"St. Martin","PM":"St. Pierre & Miquelon","VC":"St. Vincent & Grenadines","SD":"Sudan","SR":"Suriname","SJ":"Svalbard & Jan Mayen","SE":"Sweden","CH":"Switzerland","SY":"Syria","TW":"Taiwan","TJ":"Tajikistan","TZ":"Tanzania","TH":"Thailand","TL":"Timor-Leste","TG":"Togo","TK":"Tokelau","TO":"Tonga","TT":"Trinidad & Tobago","TN":"Tunisia","TR":"Turkey","TM":"Turkmenistan","TC":"Turks & Caicos Islands","TV":"Tuvalu","UM":"U.S. Outlying Islands","VI":"U.S. Virgin Islands","UG":"Uganda","UA":"Ukraine","AE":"United Arab Emirates","GB":"United Kingdom","US":"United States","UY":"Uruguay","UZ":"Uzbekistan","VU":"Vanuatu","VA":"Vatican City","VE":"Venezuela","VN":"Vietnam","WF":"Wallis & Futuna","EH":"Western Sahara","YE":"Yemen","ZM":"Zambia","ZW":"Zimbabwe"}
    headers = []
    urls = []
    r = requests.get('https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population')
    soup = BeautifulSoup(r.content, 'html.parser')
    # soup.find("table")
    table = soup.find("table").find_all('tr')
    for row in table[2:]:
        number = row.find('th').text
        if '–' in number:
            continue
        a_tag = row.find('td').find('a')
        url = urljoin(r.url, a_tag['href'])
        name = a_tag.text
        headers.append(name)
        urls.append(url)
    return headers, urls
    # print(len(headers))
    # print(urls)
    # print(len(countries))
    # for c in countries:
    #     page_object = wikipedia.page(c, auto_suggest=False)
    #     print(page_object.url)

# wraps the two functions above and yields the communities found into a some file
def findCommunitiesOfContries():
    headers, urls = extractContriesHeaders()
    # findSimByUpdates([headers[0],headers[14]],[urls[0],urls[14]])
    # findSimByUpdates([headers[0],headers[14]],[urls[0],urls[14]])
    # findSimByUpdates(headers, urls)
    # print(headers[65:66], urls[65:66])
    headers[65] = 'Ecuadorians'
    urls[65] = 'https://en.wikipedia.org/wiki/Ecuadorians'
    headers[140] = 'Demographics of the Gambia'
    urls[140] = 'https://en.wikipedia.org/wiki/Demographics_of_the_Gambia'
    headers[169] = 'Demographics of the Bahamas'
    urls[169] = 'https://en.wikipedia.org/wiki/Demographics_of_the_Bahamas'
    headers[-1] = 'Vatican City'
    urls[-1] = 'https://en.wikipedia.org/wiki/Vatican_City'
    # print(headers)
    # return
    print(headers)
    df = pd.read_csv('SimilarComtriesByUpdates.csv', header=0, index_col=0)
    # print(df)
    # coms = findCommunites(headers, 0.1, df_np=df.to_numpy())
    # with open('communitiesResult.txt', 'w') as f:
    #     f.write(str(coms))
    # df = pd.DataFrame(coms, columns=headers, index=headers)
    # df.to_csv('SimilarComtriesByUpdatesCommunities.csv')

    findSimByUpdates(headers, urls, threshold = 0.5)
findCommunitiesOfContries()