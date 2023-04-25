import json
import pandas as pd

file_path = './data_monitoring/data_sample/'

account_list = ['yjhan99@kaist.ac.kr']
date = '2023-03-30'

DATA_QUALITY = pd.DataFrame(columns=['account','sleep','intra_heart'])
DATA_QUALITY['account'] = account_list

sleep_list = []
intra_heart_list = []

for account in account_list:
    file_name = file_path + account + '-' + date + '.json'
    print(file_name)
    with open(file_name, 'r') as file:
        data = json.load(file)
    sleep = data['sleep']
    if len(sleep) != 0:
        sleep_list.append('Yes')
    else:
        sleep_list.append('No')
    intra_heart = data['heart-intraday']
    if len(intra_heart) > 48:
        intra_heart_list.append('Enough')
    elif len(intra_heart) > 0:
        intra_heart_list.append('Little')
    else:
        intra_heart_list.append('None')

DATA_QUALITY['sleep'] = sleep_list
DATA_QUALITY['intra_heart'] = intra_heart_list

print(DATA_QUALITY)

DATA_QUALITY.to_csv('./data_monitoring/data_quality/data_quality_' + date + '.csv')