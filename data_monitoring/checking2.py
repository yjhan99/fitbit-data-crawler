import json
import pandas as pd

file_path = './data_monitoring/data_sample/'

account_list = ['iitp.inthewild.p01@kse.kaist.ac.kr',
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
                'iitp.inthewild.p19@kse.kaist.ac.kr',
                'iitp.inthewild.p20@kse.kaist.ac.kr',
                'iitp.inthewild.p21@kse.kaist.ac.kr',
                'iitp.inthewild.p22@kse.kaist.ac.kr',
                'iitp.inthewild.p23@kse.kaist.ac.kr'
                ]

date = '2023-06-25'

DATA_QUALITY = pd.DataFrame(columns=['account','sleep','intra_heart'])
DATA_QUALITY['account'] = account_list

sleep_list = []
intra_heart_list = []

for account in account_list:
    file_name = file_path + account + '-' + date + '.json'

    try:
        with open(file_name, 'r') as file:
            data = json.load(file)

    except FileNotFoundError:
        sleep_list.append('No')
        intra_heart_list.append('Less than 12hr')
    
    else:
        sleep = data['sleep']
        if len(sleep) != 0: # 수면시 착용 여부 확인
            sleep_list.append('Yes')
        else:
            sleep_list.append('No')

        intra_heart = data['heart-intraday']
        if len(intra_heart) > 48: # 12시간 이상 착용 여부 확인
            intra_heart_list.append('More than 12hr')
        else:
            intra_heart_list.append('Less than 12hr')

DATA_QUALITY['sleep'] = sleep_list
DATA_QUALITY['intra_heart'] = intra_heart_list

DATA_QUALITY.to_csv('./data_monitoring/data_quality2/data_quality2_' + date + '.csv')