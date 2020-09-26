import yaml
import os
from collections import defaultdict
from collections import Counter

import pandas as pd
import pickle

"""
TODO:
1. make sure you're only considering ODI  matches
2. get 2 dataframes for Sharma and Kohli
    batsman2, total_runs, total_deliveries, runs_sharma
3. get all partnerships >= 30 runs
"""
sPath = '/Users/arnab/repos/cricket-analysis-rohit-virat-partnership/india-male'
indian_innings = {}
partnerships = defaultdict(Counter)

for sChild in os.listdir(sPath):
    sChildPath = os.path.join(sPath, sChild)
    print(f"file name is {sChild}")
    if sChildPath[-4:] == 'yaml':
        match_abandoned = False
        match_type = ''
        with open(sChildPath) as fp:
            documents = yaml.full_load(fp)
            for item, doc in documents.items():
                if item == "info":
                    # print(documents[item]["outcome"])
                    match_date = str(documents[item]['dates'][0])
                    match_type = documents[item]['match_type']
                    if "winner" not in documents[item]["outcome"]:
                        match_abandoned = True
                        break

                if item == "innings":
                    # print(item, ":", doc, "\n")
                    first_innings = documents['innings'][0]['1st innings']
                    second_innings = documents['innings'][1]['2nd innings']
                    if first_innings['team'] == 'India':
                        indian_innings = first_innings
                    else:
                        indian_innings = second_innings

            # print(indian_innings)
            if not match_abandoned and match_type == 'ODI':
                for ball_dict in indian_innings['deliveries']:
                    for ball_number, ball_info in ball_dict.items():
                        b1 = ball_info['batsman']
                        b2 = ball_info['non_striker']
                        batters = None
                        if ((b1 == 'RG Sharma' and b2 == 'V Kohli') or
                            (b1 == 'V Kohli' and b2 == 'RG Sharma')):
                            batters = ('RG Sharma', 'V Kohli', match_date)
                        elif b1 == 'RG Sharma' or b1 == 'V Kohli':
                            batters = (b1, b2, match_date)
                        elif b2 == 'RG Sharma' or b2 == 'V Kohli':
                            batters = (b2, b1, match_date)
                        if batters:
                            runs = ball_info['runs']['total']
                            partnerships[batters]['partner'] = batters[1]
                            partnerships[batters]['dom'] = batters[2]
                            partnerships[batters]['total_runs'] += runs
                            partnerships[batters]['total_deliveries'] += 1
                            if b1 == 'RG Sharma':
                                runs_sharma = ball_info['runs']['batsman']
                                partnerships[batters]['runs_sharma'] += runs_sharma
                            if b1 == 'V Kohli':
                                runs_kohli = ball_info['runs']['batsman']
                                partnerships[batters]['runs_kohli'] += runs_kohli

df_sharma = []
df_kohli = []
for key in partnerships:
    if key[0] == 'RG Sharma': #and partnerships[key]['total_runs'] >= 30:
        df_sharma.append(partnerships[key])
    if key[0] == 'V Kohli': #and partnerships[key]['total_runs'] >= 30:
        df_kohli.append(partnerships[key])
        # print(f"{key} -> {partnerships[key]}\n")
df_sharma = pd.DataFrame(df_sharma)
df_kohli = pd.DataFrame(df_kohli)

print(df_sharma.head())
print("===========")
print(df_kohli.head())

# write to pickle file
with open('sharma.pkl', 'wb') as fp:
    fp.write(pickle.dumps(df_sharma, protocol=4))


with open('kohli.pkl', 'wb') as fp:
    fp.write(pickle.dumps(df_kohli, protocol=4))
                
