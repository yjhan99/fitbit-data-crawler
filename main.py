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
_ACCOUNTS = dict()

'''
A path for selenium chrome driver
'''
_SELENIUM_PATH = ''

'''
Client ID of your OAuth2 webapp
'''
_CLIENT_ID = ''

'''
Client secret of your OAuth2 webapp
'''
_CLIENT_SECRET = ''

'''
Callback URL of your OAuth2 webapp
'''
_CALLBACK = ''

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
_START_DATE = ''

'''
The last date that you want to get data. 
It needs to be formatted as "YYYY-MM-DD"
'''
_END_DATE = ''

'''
The path that data are stored.
'''
_PATH_DATA = ''

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
           flag_intraday=_FLAG_INTRADAY
       )
       try:
           executor.submit(_run, retriever, uid, _START_DATE, _END_DATE, _PATH_DATA)
           time.sleep(300)
       except Exception:
           import traceback
           print(f'[MAIN] Error occurred in {uid}/{pw}. Caused by:')
           traceback.print_exc()

       executor.shutdown(True)
