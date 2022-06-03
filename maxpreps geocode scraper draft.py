import requests
from lxml import html
from time import sleep
import pandas as pd
import re

#To use this script, you need a geocodes api from google.  To get one, go to www.developers.google.com.
# Register an application, grab a geocodes api.  Insert the code between the '' in YOUR_API_KEY = '' below.
#This will give you coordinates for most schools as well as the school address.

def maxpreps_geocoords(maxpreps_high_school_name, state):
    YOUR_API_KEY = ''
    high_school_name = maxpreps_high_school_name + ' high school'
    if '(' in high_school_name:
        hometown2 = re.findall(r'\(.*?\)', high_school_name)[0].strip(' (').strip(')')
        step2 = re.findall(r'\(.*?\)', high_school_name)[0]
        high_school_name2 = high_school_name.replace(step2,'')
        stem = high_school_name2 + ',' + hometown2 + ',' + state
    else:
        stem = high_school_name + ',' + state
    address = stem.replace('  ',' ')
    address = address.replace(' ','+')
    print(address,file=open('stems3.csv','a'))
    print(address)
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=' + YOUR_API_KEY
    payload={}    
    response = requests.request("GET", url, data=payload)
    return response.json()
#Enter the name of the state, you can also enter make the list longer than one
#states = ['florida','georgia','california','texas','ohio']
states = ['florida']
#the script works for multiple sports
#['baseball','basketball','football']
sports = ['football']

#multiple years can be scraped as well
#years = [15,16,17,18,19,20]
years = [21]


page = 1
teams_on_page = 26

profiles_list = []
df = {'maxpreps_high_school_name':'','maxpreps_high_school_url':'','maxpreps_address_input':'','maxpreps_address':'','maxpreps_coords':'','maxpreps_team_record':'','maxpreps_team_rating':'','maxpreps_team_opponent_rating':'','maxpreps_lat':'','maxpreps_lng':'','maxpreps_address':'','year':'','state':'','sport':''}

total = 0
while teams_on_page > 1:
    for sport in sports:
        for state in states:
            for year in years:
                sleep(1)
                
                url = 'https://www.maxpreps.com/rankings/' + sport + '-' + str(year) + '/' + str(page) + '/state/' + state + '.htm'
                #print(url)
                headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36'}
                recruit_url = requests.get(url, headers=headers)
                #print(f' HTTP Status: {recruit_url.status_code}')
                root = html.fromstring(recruit_url.content)
                teams_on_page = len(root.xpath('//*[@id="rankings"]/tbody/tr'))+1
                #print('teams on page: ' + str(teams_on_page))
                for row in range(1,teams_on_page):
                    maxpreps_high_school_name = root.xpath('//*[@id="rankings"]/tbody/tr[' + str(row) + ']/th/a/text()')[0]
                    df['maxpreps_high_school_name'] = root.xpath('//*[@id="rankings"]/tbody/tr[' + str(row) + ']/th/a/text()')[0]
                    df['maxpreps_high_school_url'] = root.xpath('//*[@id="rankings"]/tbody/tr[' + str(row) + ']/th/a/@href')[0]
                    df['maxpreps_team_record'] = root.xpath('//*[@id="rankings"]/tbody/tr[' + str(row) + ']/td[2]/text()')[0]
                    df['maxpreps_team_rating'] = root.xpath('//*[@id="rankings"]/tbody/tr[' + str(row) + ']/td[3]/text()')[0]
                    df['maxpreps_team_opponent_rating'] = root.xpath('//*[@id="rankings"]/tbody/tr[' + str(row) + ']/td[4]/text()')[0]
                    maxpreps_coords = maxpreps_geocoords(maxpreps_high_school_name, state)
                    try:
                        high_school_name = maxpreps_high_school_name + ' high school'
                        address = high_school_name.replace(' ','+')
                        df['maxpreps_address_input'] = address
                    except:
                        df['maxpreps_address'] = ''
                    try:
                        df['maxpreps_coords'] = str(maxpreps_coords[0])
                    except:
                        df['maxpreps_coords'] = ''
                    try:
                        df['maxpreps_address'] = str(maxpreps_coords[1])
                    except:
                        df['maxpreps_address'] = ''
                    try:
                        df['maxpreps_lat'] = maxpreps_coords['results'][0]['geometry']['location']['lat']
                    except:
                        df['maxpreps_lat'] = ''
                    try:
                        df['maxpreps_lng'] = maxpreps_coords['results'][0]['geometry']['location']['lng']
                    except:
                        df['maxpreps_lng'] = ''
                    try:
                        df['maxpreps_address'] = maxpreps_coords['results'][0]['formatted_address']
                    except:
                        df['maxpreps_address'] = ''
                    try:
                        df['sport'] = sport
                    except:
                        df['sport'] = ''
                    try:
                        df['state'] = state
                    except:
                        df['state'] = ''
                    try:
                        df['year'] = str(year)
                    except:
                        df['year'] = ''

                    profiles_list.append(df.copy())
                    total += 1
                    print(total)
                page += 1

pd.DataFrame.from_dict(profiles_list).to_csv('maxpreps_' + str(years) + '_' + str(sports) + '_' + str(states) + '_geocodes.csv',index=False)

    
