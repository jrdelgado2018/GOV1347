import pandas as pd
from bs4 import BeautifulSoup
import urllib3

http = urllib3.PoolManager()

links = {
    2008 : "https://www.cookpolitical.com/ratings/house-race-ratings/139081",
    2012 : "https://www.cookpolitical.com/ratings/house-race-ratings/139120",
    2014 : "https://www.cookpolitical.com/ratings/house-race-ratings/139260",
    2016 : "https://www.cookpolitical.com/ratings/house-race-ratings/139363",
    2018 : "https://www.cookpolitical.com/ratings/house-race-ratings/187562",
    2020 : "https://www.cookpolitical.com/ratings/house-race-ratings/230686",
    2022 : "https://www.cookpolitical.com/ratings/house-race-ratings"
}

race_lst = []
for year in links.keys():
    response = http.request('GET', links[year])
    soup = BeautifulSoup(response.data, 'lxml')
    table = soup.find('div', {'id' : 'block-politicalreport-content'})
    categories = {
        'Solid D' : table.find('div', {'id' : 'solid-seats-d'}),
        'Likely D' : table.find('div', {'id' : 'modal-from-table-likely-d'}),
        'Lean D' : table.find('div', {'id' : 'modal-from-table-lean-d'}),
        'Tossup D' : table.find('div', {'id' : 'modal-from-table-tossup-d'}),
        'Solid R' : table.find('div', {'id' : 'solid-seats-r'}),
        'Likely R' : table.find('div', {'id' : 'modal-from-table-likely-r'}),
        'Lean R' : table.find('div', {'id' : 'modal-from-table-lean-r'}),
        'Tossup R' : table.find('div', {'id' : 'modal-from-table-tossup-r'})
    }
    for cat in categories.keys():
        races = categories[cat].find_all('div', {'class' : 'popup-table-data-row'})
        for race in races[1:]:
            state_district = race.a.text.strip()
            race_lst.append({
                "year" : year,
                "state" : state_district[:2],
                "district" : state_district[-2:],
                "inc_party" : race.a['class'][1][:3],
                "description" : cat
            })

df = pd.DataFrame(race_lst)

fips = {
    "AL" : 1, "AK" : 2, "AZ" : 4, "AR" : 5, "CA" : 6, "CO" : 8, "CT" : 9, "DE" : 10, "FL" : 12, "GA" : 13,
    "HI" : 15, "ID" : 16, "IL" : 17, "IN" : 18, "IA" : 19, "KS" : 20, "KY" : 21, "LA" : 22, "ME" : 23, "MD" : 24,
    "MA" : 25, "MI" : 26, "MN" : 27, "MS" : 28, "MO" : 29, "MT" : 30, "NE" : 31, "NV" : 32, "NH" : 33, "NJ" : 34,
    "NM" : 35, "NY" : 36, "NC" : 37, "ND" : 38, "OH" : 39, "OK" : 40, "OR" : 41, "PA" : 42, "RI" : 44, "SC" : 45,
    "SD" : 46, "TN" : 47, "TX" : 48, "UT" : 49, "VT" : 50, "VA" : 51, "WA" : 53, "WV" : 54, "WI" : 55, "WY" : 56
}
df["geoid"] = df.apply(lambda row : str(fips[row.state]) + row.district, axis=1)

codes = {
        'Solid D' : 4,
        'Likely D' : 3,
        'Lean D' : 2,
        'Tossup D' : 1,
        'Solid R' : -4,
        'Likely R' : -3,
        'Lean R' : -2,
        'Tossup R' : -1
}
df["code"] = df.apply(lambda row : codes[row.description], axis=1)

df.to_csv("cook.csv")