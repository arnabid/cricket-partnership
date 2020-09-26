import yaml
import os
from collections import defaultdict
from collections import Counter
import time

import pandas as pd
import pickle

# start time of script
start = time.perf_counter()

sPath = '/Users/arnab/repos/cricket-analysis-rohit-virat-partnership/india_male'
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
count = 0

for sChild in os.listdir(sPath):
    sChildPath = os.path.join(sPath, sChild)
    print(f"file name: {sChild}")

    # only read yaml files
    if sChildPath[-4:] == 'yaml':
        match_abandoned = False
        venue = ''
        match_type = ''
        winner = ''
        winner_toss = ''
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

            if not match_abandoned and match_type == 'ODI':
                rs_prtnrs, vk_prtnrs = set(), set()
                for ball_dict in indian_innings['deliveries']:
                    for ball_number, ball_info in ball_dict.items():
                        b1 = ball_info['batsman']
                        b2 = ball_info['non_striker']
                        runs = ball_info['runs']['total']
                        key = (b1, b2)
                        if 'RG Sharma' in key:
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
                        if 'V Kohli' in key:
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
                for vk_pkey in vk_prtnrs:
                    partnerships[vk_pkey]['dom'] = match_date
                    partnerships[vk_pkey]['result'] = 1 if winner == 'India' else 0
                    partnerships[vk_pkey]['home_venue'] = 1 if venue in home_venues else 0
                    partnerships[vk_pkey]['win_toss'] = 1 if winner_toss == 'India' else 0
                        

df_sharma = []
df_kohli = []

for key in partnerships:
    # print(key)
    # print(partnerships[key])
    # print("=====================")
    if key[0] == 'RG Sharma': #and partnerships[key]['total_runs'] >= 30:
        df_sharma.append(partnerships[key])
    if key[0] == 'V Kohli': #and partnerships[key]['total_runs'] >= 30:
        df_kohli.append(partnerships[key])
        # print(f"{key} -> {partnerships[key]}\n")
df_sharma = pd.DataFrame(df_sharma)
df_kohli = pd.DataFrame(df_kohli)

# print(df_sharma.head())
# print("===========")
# print(df_kohli.head())

# write to pickle files
with open('sharma.pkl', 'wb') as fp:
    fp.write(pickle.dumps(df_sharma, protocol=4))

with open('kohli.pkl', 'wb') as fp:
    fp.write(pickle.dumps(df_kohli, protocol=4))

# print run time
end = time.perf_counter()
print(f"Finished in {round(end-start)} second(s)")