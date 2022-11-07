import pandas as pd
from bs4 import BeautifulSoup
import urllib3

http = urllib3.PoolManager()

links = {
    2010 : "https://insideelections.com/api/xml/ratings/by-id/house/1424",
    2012 : "https://insideelections.com/api/xml/ratings/by-id/house/2160",
    2014 : "https://insideelections.com/api/xml/ratings/by-id/house/2867",
    2016 : "https://insideelections.com/api/xml/ratings/by-id/house/3464",
    2018 : "https://insideelections.com/api/xml/ratings/by-id/house/4097",
    2020 : "https://insideelections.com/api/xml/ratings/by-id/house/4588",
    2022 : "https://insideelections.com/api/xml/ratings/house"
}

race_lst = []
for year in links.keys():
    response = http.request('GET', links[year])
    soup = BeautifulSoup(response.data, 'lxml')
    races = soup.find_all("race")
    for race in races:
        race_lst.append({
            "year" : year,
            "state" : race.state.text,
            "district" : "00" if race.state.text in ["AK", "DE", "MT", "ND", "SD", "VT", "WY"] else ("0" if len(race.district.text) == 1 else "") + race.district.text,
            "inc_party" : race.party.text, 
            "is_open" : race.open.text, 
            "description" : race.rating.label.text
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
    'Currently Safe Republican' : -4,
    'Republican Favored' : -3,
    'Lean Republican' : -2,
    'Toss-up/Tilt Republican' : -1, 
    'Pure Toss-up' : 0,
    'Currently Safe Democrat' : 4,
    'Democrat Favored' : 3,
    'Lean Democrat' : 2,
    'Toss-up/Tilt Democrat' : 1
}
df["code"] = df.apply(lambda row : codes[row.description], axis=1)

df.to_csv("inside_elections.csv")