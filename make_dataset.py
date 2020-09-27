import os
import pickle
import time
from collections import Counter, defaultdict

import pandas as pd
import yaml

"""
result date structure after reading a yaml file - partnerships

partnerships is a dict
key = ('RG Sharma', 'partner', 'date_of_match') and/or ('V Kohli', 'partner', 'date_of_match')
value = {
            'partner': , # the other batsman in the partnership
            'total_runs': , # the total runs scored in the partnership
            'total_deliveries': , # the total balls faced by both batsman during the partnership
            'runs_sharma': , # runs scored by RG Sharma in the partnership
            'dom': , # the date of the match
            'result': , # the result of the match 1 if India won, 0 otherwise (loss/tied/no-result)
            'home_venue': , # was the match played in India or international venue?
            'win_toss': , # did India win the toss? 1 if yes else 0
            'bat_first':  did India bat first? 1 if yes else 0
        }
"""

# start time of script
start = time.perf_counter()

# location of the yaml files
sPath = '/Users/arnab/repos/cricket-analysis-rohit-virat-partnership/odi_files'

# international cricket venues in India
home_venues = set(['Ahmedabad',
                'Dharmasala',
                'Mumbai',
                'Visakhapatnam',
                'Pune',
                'Bangalore',
                'Jaipur',
                'Mirpur',
                'Cuttack',
                'Jamshedpur',
                'Guwahati',
                'Dharamsala',
                'Thiruvananthapuram',
                'Chandigarh',
                'Kochi',
                'Hyderabad',
                'Rajkot',
                'Delhi',
                'Bengaluru',
                'Vadodara',
                'Nagpur',
                'Ranchi',
                'Indore',
                'Kanpur',
                'Chennai',
                'Gwalior',
                'Kolkata'
                ])

indian_innings = {}
partnerships = defaultdict(Counter)

for sChild in os.listdir(sPath):
    sChildPath = os.path.join(sPath, sChild)

    # only read yaml files
    if sChildPath[-4:] == 'yaml':
        match_abandoned = False
        venue = ''
        match_type = ''
        winner = ''
        winner_toss = ''
        india_bat_first = 1
        with open(sChildPath) as fp:
            documents = yaml.full_load(fp)
            for item, doc in documents.items():
                if item == "info":
                    match_date = str(documents[item]['dates'][0])
                    match_type = documents[item]['match_type']
                    winner_toss = documents[item]['toss']['winner']
                    if 'city' in documents[item]:
                        venue = documents[item]['city']
                    elif 'venue' in documents[item]:
                        venue = documents[item]['venue']
                    if "winner" not in documents[item]["outcome"]:
                        match_abandoned = True
                        break
                    else:
                        winner = documents[item]["outcome"]['winner']

                if item == "innings":
                    first_innings = documents['innings'][0]['1st innings']
                    second_innings = documents['innings'][1]['2nd innings']
                    if first_innings['team'] == 'India':
                        indian_innings = first_innings
                    else:
                        indian_innings = second_innings
                        india_bat_first = 0

            if not match_abandoned and match_type == 'ODI':
                rs_prtnrs, vk_prtnrs = set(), set()
                for ball_dict in indian_innings['deliveries']:
                    for ball_number, ball_info in ball_dict.items():
                        b1 = ball_info['batsman']
                        b2 = ball_info['non_striker']
                        runs = ball_info['runs']['total']
                        batsmen = (b1, b2)
                        if 'RG Sharma' in batsmen:
                            runs_sharma = 0
                            non_striker = b1
                            if b1 == 'RG Sharma':
                                non_striker = b2
                                runs_sharma = ball_info['runs']['batsman']
                            rs_key = ('RG Sharma', non_striker, match_date)
                            rs_prtnrs.add(rs_key)
                            partnerships[rs_key]['partner'] = rs_key[1]
                            partnerships[rs_key]['total_runs'] += runs
                            partnerships[rs_key]['total_deliveries'] += 1
                            partnerships[rs_key]['runs_sharma'] += runs_sharma
                        if 'V Kohli' in batsmen:
                            runs_kohli = 0
                            non_striker = b1
                            if b1 == 'V Kohli':
                                non_striker = b2
                                runs_kohli = ball_info['runs']['batsman']
                            vk_key = ('V Kohli', non_striker, match_date)
                            vk_prtnrs.add(vk_key)
                            partnerships[vk_key]['partner'] = vk_key[1]
                            partnerships[vk_key]['total_runs'] += runs
                            partnerships[vk_key]['total_deliveries'] += 1
                            partnerships[vk_key]['runs_kohli'] += runs_kohli
                for rs_pkey in rs_prtnrs:
                    partnerships[rs_pkey]['dom'] = match_date
                    partnerships[rs_pkey]['result'] = 1 if winner == 'India' else 0
                    partnerships[rs_pkey]['home_venue'] = 1 if venue in home_venues else 0
                    partnerships[rs_pkey]['win_toss'] = 1 if winner_toss == 'India' else 0
                    partnerships[rs_pkey]['bat_first'] = india_bat_first
                for vk_pkey in vk_prtnrs:
                    partnerships[vk_pkey]['dom'] = match_date
                    partnerships[vk_pkey]['result'] = 1 if winner == 'India' else 0
                    partnerships[vk_pkey]['home_venue'] = 1 if venue in home_venues else 0
                    partnerships[vk_pkey]['win_toss'] = 1 if winner_toss == 'India' else 0
                    partnerships[vk_pkey]['bat_first'] = india_bat_first
                        

df_sharma = []
df_kohli = []

for key in partnerships:
    if key[0] == 'RG Sharma':
        df_sharma.append(partnerships[key])
    if key[0] == 'V Kohli':
        df_kohli.append(partnerships[key])

# dataframes
df_sharma = pd.DataFrame(df_sharma)
df_kohli = pd.DataFrame(df_kohli)

# write to pickle files
with open('sharma.pkl', 'wb') as fp:
    fp.write(pickle.dumps(df_sharma, protocol=4))

with open('kohli.pkl', 'wb') as fp:
    fp.write(pickle.dumps(df_kohli, protocol=4))

# print run time
end = time.perf_counter()
print(f"Finished in {round(end-start)} second(s)")
