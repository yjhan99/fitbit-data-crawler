import json
import pandas as pd
from datetime import datetime, time

file_path = './data_monitoring/data_sample/'

date = '2023-06-25'

# account_list = ['iitp.inthewild.p01@kse.kaist.ac.kr',
#                 'iitp.inthewild.p02@kse.kaist.ac.kr',
#                 'iitp.inthewild.p03@kse.kaist.ac.kr',
#                 'iitp.inthewild.p04@kse.kaist.ac.kr',
#                 'iitp.inthewild.p05@kse.kaist.ac.kr',
#                 'iitp.inthewild.p06@kse.kaist.ac.kr',
#                 'iitp.inthewild.p07@kse.kaist.ac.kr',
#                 'iitp.inthewild.p08@kse.kaist.ac.kr',
#                 'iitp.inthewild.p09@kse.kaist.ac.kr',
#                 'iitp.inthewild.p10@kse.kaist.ac.kr',
#                 'iitp.inthewild.p11@kse.kaist.ac.kr',
#                 'iitp.inthewild.p12@kse.kaist.ac.kr',
#                 'iitp.inthewild.p13@kse.kaist.ac.kr',
#                 'iitp.inthewild.p14@kse.kaist.ac.kr',
#                 'iitp.inthewild.p15@kse.kaist.ac.kr',
#                 'iitp.inthewild.p16@kse.kaist.ac.kr',
#                 'iitp.inthewild.p17@kse.kaist.ac.kr',
#                 'iitp.inthewild.p18@kse.kaist.ac.kr',
#                 'iitp.inthewild.p19@kse.kaist.ac.kr',
#                 'iitp.inthewild.p20@kse.kaist.ac.kr',
#                 'iitp.inthewild.p21@kse.kaist.ac.kr',
#                 'iitp.inthewild.p22@kse.kaist.ac.kr',
#                 'iitp.inthewild.p23@kse.kaist.ac.kr'
#                 ]

account_list_8_17 = [

]

account_list_9_18 = [
    'iitp.inthewild.p19@kse.kaist.ac.kr',
    'iitp.inthewild.p21@kse.kaist.ac.kr',
    'iitp.inthewild.p22@kse.kaist.ac.kr'
]

account_list_10_19 = [

]

account_list_11_20 = [

]

account_list_12_21 = [

]

account_list_half = [

] # 반차

account_list_none = [
    'iitp.inthewild.p01@kse.kaist.ac.kr',
    'iitp.inthewild.p02@kse.kaist.ac.kr',
    'iitp.inthewild.p03@kse.kaist.ac.kr',
    'iitp.inthewild.p04@kse.kaist.ac.kr',
    'iitp.inthewild.p05@kse.kaist.ac.kr',
    'iitp.inthewild.p06@kse.kaist.ac.kr',
    'iitp.inthewild.p07@kse.kaist.ac.kr',
    'iitp.inthewild.p08@kse.kaist.ac.kr',
    'iitp.inthewild.p09@kse.kaist.ac.kr',
    'iitp.inthewild.p10@kse.kaist.ac.kr',
    'iitp.inthewild.p11@kse.kaist.ac.kr',
    'iitp.inthewild.p12@kse.kaist.ac.kr',
    'iitp.inthewild.p13@kse.kaist.ac.kr',
    'iitp.inthewild.p14@kse.kaist.ac.kr',
    'iitp.inthewild.p15@kse.kaist.ac.kr',
    'iitp.inthewild.p16@kse.kaist.ac.kr',
    'iitp.inthewild.p17@kse.kaist.ac.kr',
    'iitp.inthewild.p18@kse.kaist.ac.kr',
    'iitp.inthewild.p20@kse.kaist.ac.kr',
    'iitp.inthewild.p23@kse.kaist.ac.kr'
] # 보건 / 연차 / 주말

DATA_QUALITY = pd.DataFrame(columns=['account','intra_heart_len','intra_heart'])

account_list = []
intra_heart_len_list = []
intra_heart_list = []

for account in account_list_8_17:
    file_name = file_path + account + '-' + date + '.json'

    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            intra_heart = pd.json_normalize(data['heart-intraday'])
    
    except FileNotFoundError:
        account_list.append(account)
        intra_heart_len_list.append(0)
        intra_heart_list.append('Less than 50%')

    else:
        if (len(intra_heart) == 0):
            account_list.append(account)
            intra_heart_len_list.append(len(intra_heart))
            intra_heart_list.append('Less than 50%')
            continue

        intra_heart['time'] = pd.to_datetime(intra_heart['time'], format='%H:%M:%S').dt.time
        intra_heart = intra_heart.loc[((intra_heart['time'] > time(8,00,00)) & (intra_heart['time'] < time(17,0,0))),:]

        account_list.append(account)
        intra_heart_len_list.append(len(intra_heart))

        if len(intra_heart) > 36 * 0.7:
            intra_heart_list.append('More than 70%')
        elif len(intra_heart) > 36 * 0.5:
            intra_heart_list.append('More than 50%')
        else:
            intra_heart_list.append('Less than 50%')

for account in account_list_9_18:
    file_name = file_path + account + '-' + date + '.json'

    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            intra_heart = pd.json_normalize(data['heart-intraday'])
    
    except FileNotFoundError:
        account_list.append(account)
        intra_heart_len_list.append(0)
        intra_heart_list.append('Less than 50%')
    
    else:
        if (len(intra_heart) == 0):
            account_list.append(account)
            intra_heart_len_list.append(len(intra_heart))
            intra_heart_list.append('Less than 50%')
            continue

        intra_heart['time'] = pd.to_datetime(intra_heart['time'], format='%H:%M:%S').dt.time
        intra_heart = intra_heart.loc[((intra_heart['time'] > time(9,00,00)) & (intra_heart['time'] < time(18,0,0))),:]

        account_list.append(account)
        intra_heart_len_list.append(len(intra_heart))

        if len(intra_heart) > 36 * 0.7:
            intra_heart_list.append('More than 70%')
        elif len(intra_heart) > 36 * 0.5:
            intra_heart_list.append('More than 50%')
        else:
            intra_heart_list.append('Less than 50%')

for account in account_list_10_19:
    file_name = file_path + account + '-' + date + '.json'

    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            intra_heart = pd.json_normalize(data['heart-intraday'])
    
    except FileNotFoundError:
        account_list.append(account)
        intra_heart_len_list.append(0)
        intra_heart_list.append('Less than 50%')

    else:
        if (len(intra_heart) == 0):
            account_list.append(account)
            intra_heart_len_list.append(len(intra_heart))
            intra_heart_list.append('Less than 50%')
            continue

        intra_heart['time'] = pd.to_datetime(intra_heart['time'], format='%H:%M:%S').dt.time
        intra_heart = intra_heart.loc[((intra_heart['time'] > time(10,00,00)) & (intra_heart['time'] < time(19,0,0))),:]

        account_list.append(account)
        intra_heart_len_list.append(len(intra_heart))

        if len(intra_heart) > 36 * 0.7:
            intra_heart_list.append('More than 70%')
        elif len(intra_heart) > 36 * 0.5:
            intra_heart_list.append('More than 50%')
        else:
            intra_heart_list.append('Less than 50%')

for account in account_list_11_20:
    file_name = file_path + account + '-' + date + '.json'

    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            intra_heart = pd.json_normalize(data['heart-intraday'])
    
    except FileNotFoundError:
        account_list.append(account)
        intra_heart_len_list.append(0)
        intra_heart_list.append('Less than 50%')

    else:
        if (len(intra_heart) == 0):
            account_list.append(account)
            intra_heart_len_list.append(len(intra_heart))
            intra_heart_list.append('Less than 50%')
            continue

        intra_heart['time'] = pd.to_datetime(intra_heart['time'], format='%H:%M:%S').dt.time
        intra_heart = intra_heart.loc[((intra_heart['time'] > time(11,00,00)) & (intra_heart['time'] < time(20,0,0))),:]

        account_list.append(account)
        intra_heart_len_list.append(len(intra_heart))

        if len(intra_heart) > 36 * 0.7:
            intra_heart_list.append('More than 70%')
        elif len(intra_heart) > 36 * 0.5:
            intra_heart_list.append('More than 50%')
        else:
            intra_heart_list.append('Less than 50%')

for account in account_list_12_21:
    file_name = file_path + account + '-' + date + '.json'

    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            intra_heart = pd.json_normalize(data['heart-intraday'])
    
    except FileNotFoundError:
        account_list.append(account)
        intra_heart_len_list.append(0)
        intra_heart_list.append('Less than 50%')

    else:
        if (len(intra_heart) == 0):
            account_list.append(account)
            intra_heart_len_list.append(len(intra_heart))
            intra_heart_list.append('Less than 50%')
            continue

        intra_heart['time'] = pd.to_datetime(intra_heart['time'], format='%H:%M:%S').dt.time
        intra_heart = intra_heart.loc[((intra_heart['time'] > time(12,00,00)) & (intra_heart['time'] < time(21,0,0))),:]

        account_list.append(account)
        intra_heart_len_list.append(len(intra_heart))

        if len(intra_heart) > 36 * 0.7:
            intra_heart_list.append('More than 70%')
        elif len(intra_heart) > 36 * 0.5:
            intra_heart_list.append('More than 50%')
        else:
            intra_heart_list.append('Less than 50%')

for account in account_list_half:
    file_name = file_path + account + '-' + date + '.json'

    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            intra_heart = pd.json_normalize(data['heart-intraday'])
    
    except FileNotFoundError:
        account_list.append(account)
        intra_heart_len_list.append(0)
        intra_heart_list.append('Less than 50%')

    else:
        if (len(intra_heart) == 0):
            account_list.append(account)
            intra_heart_len_list.append(len(intra_heart))
            intra_heart_list.append('Less than 50%')
            continue

        intra_heart['time'] = pd.to_datetime(intra_heart['time'], format='%H:%M:%S').dt.time
        intra_heart = intra_heart.loc[((intra_heart['time'] > time(9,00,00)) & (intra_heart['time'] < time(13,30,0))),:] # 반차 시간이 정확히 언제인지 몰라서 수정해야할 수도 있습니다

        account_list.append(account)
        intra_heart_len_list.append(len(intra_heart))

        if len(intra_heart) > 18 * 0.7:
            intra_heart_list.append('More than 70%')
        elif len(intra_heart) > 18 * 0.5:
            intra_heart_list.append('More than 50%')
        else:
            intra_heart_list.append('Less than 50%')

for account in account_list_none:
    file_name = file_path + account + '-' + date + '.json'

    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            intra_heart = pd.json_normalize(data['heart-intraday'])
    
    except FileNotFoundError:
        account_list.append(account)
        intra_heart_len_list.append(0)
        intra_heart_list.append('Vacation')

    else:
        if (len(intra_heart) == 0):
            account_list.append(account)
            intra_heart_len_list.append(len(intra_heart))
            intra_heart_list.append('Vacation')
            continue

        intra_heart['time'] = pd.to_datetime(intra_heart['time'], format='%H:%M:%S').dt.time

        account_list.append(account)
        intra_heart_len_list.append(len(intra_heart)) # 그냥 하루동안 얼마나 착용했는지 확인하는 코드로 짰습니다

        intra_heart_list.append('Vacation')

DATA_QUALITY['account'] = account_list
DATA_QUALITY['intra_heart_len'] = intra_heart_len_list
DATA_QUALITY['intra_heart'] = intra_heart_list

DATA_QUALITY = DATA_QUALITY.sort_values(by='account', ascending=True)
DATA_QUALITY = DATA_QUALITY.reset_index(drop=True)

# print(DATA_QUALITY)

DATA_QUALITY.to_csv('./data_monitoring/data_quality1/data_quality1_' + date + '.csv')