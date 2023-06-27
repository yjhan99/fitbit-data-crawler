import hashlib
import os.path
from datetime import datetime, timedelta
import json
from concurrent.futures import ThreadPoolExecutor
from retriever import FitbitDataRetriever
import time



'''
Users' account information, in which 
a key is an email address and a value is a password.
'''
# _ACCOUNTS = dict(uid='yjhan99@kaist.ac.kr', pw='soend1d2d3!')
_ACCOUNTS = {
    'iitp.inthewild.p01@kse.kaist.ac.kr':'ZUr2Cd.GQ',
    'iitp.inthewild.p02@kse.kaist.ac.kr':'eEh{Q8Pp@',
    'iitp.inthewild.p03@kse.kaist.ac.kr':'zF?v_3#q6',
    'iitp.inthewild.p04@kse.kaist.ac.kr':'e%H&#(5vn',
    'iitp.inthewild.p05@kse.kaist.ac.kr':'gyj3.EfNC',
    'iitp.inthewild.p06@kse.kaist.ac.kr':'Tzky4K?g8',
    'iitp.inthewild.p07@kse.kaist.ac.kr':'eJxNB94-G',
    'iitp.inthewild.p08@kse.kaist.ac.kr':'cZ&5[Mf@j',
    'iitp.inthewild.p09@kse.kaist.ac.kr':'WE47_5Mm@',
    'iitp.inthewild.p10@kse.kaist.ac.kr':'k"Af5Lc2W',
    'iitp.inthewild.p11@kse.kaist.ac.kr':'etc@~4T(q',
    'iitp.inthewild.p12@kse.kaist.ac.kr':'m6M9^s4TK',
    'iitp.inthewild.p13@kse.kaist.ac.kr':'Nv6E!fKeC',
    'iitp.inthewild.p14@kse.kaist.ac.kr':'Df5HP!RcG',
    'iitp.inthewild.p15@kse.kaist.ac.kr':'W$V4c(T%L',
    'iitp.inthewild.p16@kse.kaist.ac.kr':'tMx&r~F3N',
    'iitp.inthewild.p17@kse.kaist.ac.kr':'j%wz6S&8q',
    'iitp.inthewild.p18@kse.kaist.ac.kr':'GBuUt4a@3',
    'iitp.inthewild.p19@kse.kaist.ac.kr':'SfKV4&Ge2',
    'iitp.inthewild.p20@kse.kaist.ac.kr':'C;^3ycgB8',
    'iitp.inthewild.p21@kse.kaist.ac.kr':'P5w9L@m%c',
    'iitp.inthewild.p22@kse.kaist.ac.kr':'m;A2b4Jg[',
    'iitp.inthewild.p23@kse.kaist.ac.kr':'L6-he@HWn'
    }

'''
A path for selenium chrome driver
'''
_SELENIUM_PATH = './chromedriver'

'''
Client ID of your OAuth2 webapp
'''
_CLIENT_ID = '23QVYH'

'''
Client secret of your OAuth2 webapp
'''
_CLIENT_SECRET = 'bf9e7579bc65903ff979db9d18e204f3'

'''
Callback URL of your OAuth2 webapp
'''
_CALLBACK = 'https://ic.kaist.ac.kr/fitbit'

'''
Interval (in seconds) between subsequent API calls. 
Note that too short interval raises IP block or request limits.
'''
_CALL_INTERVAL = 30

'''
If your webapp is allowed to access to intra-day data and you want to get them,
the below should be set as True.
'''
_FLAG_INTRADAY = True

'''
The first date that you want to get data. 
It needs to be formatted as "YYYY-MM-DD"
'''
_START_DATE = '2023-06-22'

'''
The last date that you want to get data. 
It needs to be formatted as "YYYY-MM-DD"
'''
_END_DATE = '2023-06-25'

'''
The path that data are stored.
'''
_PATH_DATA = './data_monitoring/data_sample'

'''
The number of parallel workers for getting data.
'''
_N_WORKERS = 8


def _run(
       _fitbit: FitbitDataRetriever,
       _user: str,
       _start_date: str,
       _end_date: str,
       _path: str
):
   datetime_start = datetime.strptime(_start_date, '%Y-%m-%d')
   datetime_end = datetime.strptime(_end_date, '%Y-%m-%d')
   n_days = (datetime_end - datetime_start).days + 1

   for t in range(n_days):
       date = datetime_start + timedelta(days=t)
       str_date = date.strftime("%Y-%m-%d")

       result = _fitbit.retrieve(date=str_date)
       alg = hashlib.md5()
       alg.update(_user.encode())
       result['pid'] = alg.hexdigest()
       p = os.path.join(_path, f'{_user}-{str_date}.json')
       with open(p, 'w') as f:
           json.dump(result, f)
           print(f'[MAIN] Complete. Data are stored in {p}.')


if __name__ == '__main__':
   executor = ThreadPoolExecutor(max_workers=_N_WORKERS)

   for uid, pw in _ACCOUNTS.items():
       retriever = FitbitDataRetriever(
           selenium_path=_SELENIUM_PATH,
           client_id=_CLIENT_ID,
           client_secret=_CLIENT_SECRET,
           callback=_CALLBACK,
           call_interval=_CALL_INTERVAL,
           email=uid,
           password=pw,
           flag_intraday=_FLAG_INTRADAY,
       )
       try:
           executor.submit(_run, retriever, uid, _START_DATE, _END_DATE, _PATH_DATA)
           time.sleep(300)
       except Exception:
           import traceback
           print(f'[MAIN] Error occurred in {uid}/{pw}. Caused by:')
           traceback.print_exc()

executor.shutdown(True)