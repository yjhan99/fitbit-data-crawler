from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
import urllib.parse as url_parser
import base64
import requests
import time
from datetime import datetime


def _log(*args):
    print('[{}] {}'.format(datetime.now().strftime('%y-%m-%d %H:%M:%S'), *args))


def _handle_sign_in(browser: WebDriver, email: str, password: str):
    _log(f'_handle_sign_in(email={email}, password={password})')
    input_email = browser.find_element(By.CSS_SELECTOR, '#loginForm input[type="email"]')
    input_password = browser.find_element(By.CSS_SELECTOR, '#loginForm input[type="password"]')
    button_sign_in = browser.find_element(By.CSS_SELECTOR, '#loginForm button')

    input_email.send_keys(email)
    input_password.send_keys(password)
    button_sign_in.submit()


def _check_auth_code_screen(browser: WebDriver, callback: str):
    _log(f'_check_auth_code_screen(callback={callback})')
    current_url = browser.current_url
    is_redirect = current_url.startswith(callback)
    try:
        browser.find_element(By.CSS_SELECTOR, "#selectAllScope")
        is_scope_selection = True
    except NoSuchElementException:
        is_scope_selection = False
    return is_redirect or is_scope_selection


def _get_auth_code(browser: WebDriver, callback: str) -> str:
    _log(f'_get_auth_code(callback={callback})')

    wait = WebDriverWait(browser, 120).until(
        lambda b: _check_auth_code_screen(b, callback)
    )

    if wait is not True:
        raise Exception("Not found auth_code")

    current_url = browser.current_url

    if current_url.startswith(callback):
        result = url_parser.urlparse(current_url)
        query = url_parser.parse_qs(result.query, strict_parsing=True)
        return query['code'][-1]
    else:
        browser.find_element(By.CSS_SELECTOR, "#selectAllScope").click()
        browser.find_element(By.CSS_SELECTOR, '#allow-button').click()
        return _get_auth_code(browser, callback)


def _get_simple_value(d: dict, key: str):
    if key in d and d[key]:
        return d[key][-1]['value']
    else:
        return '-'


def _get_sleep_value(d: dict, key: str):
    if key in d and d[key] and 'stages' in d[key] and d[key]['stages']:
        return d[key]['stages']
    else:
        return []


def _get_intraday_value(d: dict, key: str) -> list:
    if key in d and d[key] and 'dataset' in d[key] and d[key]['dataset']:
        return d[key]['dataset']
    else:
        return []


class FitbitDataRetriever:
    _OAUTH_AUTH_URI = "https://www.fitbit.com/oauth2/authorize"
    _OAUTH_TOKEN_ACCESS_URI = "https://api.fitbit.com/oauth2/token"

    _RESOURCE_MINUTES_SEDENTARY = 'activities/tracker/minutesSedentary'
    _RESOURCE_MINUTES_LIGHTLY_ACTIVE = 'activities/tracker/minutesLightlyActive'
    _RESOURCE_MINUTES_FAIRLY_ACTIVE = 'activities/tracker/minutesFairlyActive'
    _RESOURCE_MINUTES_VERY_ACTIVE = 'activities/tracker/minutesVeryActive'
    _RESOURCE_ACTIVITY_CALORIES = 'activities/tracker/activityCalories'

    _RESOURCE_CALORIES_INTRA = 'activities/calories'
    _RESOURCE_STEPS_INTRA = 'activities/steps'
    _RESOURCE_DISTANCE_INTRA = 'activities/distance'
    _RESOURCE_FLOORS_INTRA = 'activities/floors'
    _RESOURCE_ELEVATION_INTRA = 'activities/elevation'
    _RESOURCE_HEART_INTRA = 'activities/heart'

    _RESOURCE_SLEEP = 'sleep'

    def __init__(
            self,
            selenium_path: str,
            client_id: str,
            client_secret: str,
            callback: str,
            call_interval: int,
            email: str,
            password: str,
            flag_intraday: bool = False
    ):
        self._selenium_path = selenium_path
        self._client_id = client_id
        self._client_secret = client_secret
        self._callback = callback
        self._call_interval = call_interval
        self._email = email
        self._password = password
        self._user_id = None
        self._access_token = None
        self._refresh_token = None
        self._flag_intraday = flag_intraday

    @property
    def is_authorized(self) -> bool:
        return self._access_token and self._refresh_token and self._user_id

    @property
    def auth_url(self) -> str:
        return f'{self._OAUTH_AUTH_URI}?response_type=code&' \
               f'client_id={self._client_id}&' \
               f'redirect_uri={self._callback}&' \
               f'scope=activity%20heartrate%20profile%20sleep'

    def _update_auth_token(self, auth_code: str):
        _log(f'_update_auth_token(auth_code={auth_code})')

        id_and_secret = f'{self._client_id}:{self._client_secret}'.encode()
        auth_header = base64.encodebytes(id_and_secret).decode('utf-8').strip()

        response = requests.post(
            url=self._OAUTH_TOKEN_ACCESS_URI,
            headers={
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'client_id': self._client_id,
                'grant_type': 'authorization_code',
                'redirect_uri': self._callback,
                'code': auth_code
            }
        )

        status_code = response.status_code
        content = response.json()

        if status_code != 200:
            raise Exception(f'Authorization failed\n {content}')
        else:
            self._access_token = content['access_token']
            self._refresh_token = content['refresh_token']
            self._user_id = content['user_id']

    def _refresh_auth_token(self, refresh_token: str):
        _log(f'_refresh_auth_token(callback={refresh_token})')

        id_and_secret = f'{self._client_id}:{self._client_secret}'.encode()
        auth_header = base64.encodebytes(id_and_secret).decode('utf-8').strip()

        response = requests.post(
            url=self._OAUTH_TOKEN_ACCESS_URI,
            headers={
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
            }
        )
        status_code = response.status_code
        content = response.json()

        if status_code != 200:
            raise Exception(f'Refresh Token Failed\n {content}')
        else:
            self._access_token = content['access_token']
            self._refresh_token = content['refresh_token']
            self._user_id = content['user_id']

    def _get_data(self, url: str):
        if not self.is_authorized:
            raise Exception(f'This client is not authorized yet.')
        _log(f'_get_data(url={url})')

        time.sleep(self._call_interval)

        response = requests.get(
            url=url,
            headers={
                'Authorization': f'Bearer {self._access_token}'
            }
        )
        status_code = response.status_code
        content = response.json()
        if status_code == 200:
            return content
        elif status_code == 401 and any([error['errorType'] == 'expired_token' for error in content['errors']]):
            self._refresh_auth_token(self._refresh_token)
            return self._get_data(url)
        else:
            raise Exception(f'Error\n {content}')

    def _get_activity_data(self, user_id: str, date: str, resource: str) -> dict:
        url = f'https://api.fitbit.com/1/user/{user_id}/{resource}/date/{date}/1d.json'
        return self._get_data(url=url)

    def _get_intra_day_activity_data(self, user_id: str, date: str, resource: str) -> dict:
        url = f'https://api.fitbit.com/1/user/{user_id}/{resource}/date/{date}/1d/1min.json'
        return self._get_data(url=url)

    def _get_intra_day_heart_rate_data(self, user_id: str, date: str) -> dict:
        url = f'https://api.fitbit.com/1/user/{user_id}/{self._RESOURCE_HEART_INTRA}/date/{date}/1d/1sec.json'
        return self._get_data(url=url)

    def _get_sleep_data(self, user_id: str, date: str, resource: str) -> dict:
        url = f'https://api.fitbit.com/1.2/user/{user_id}/{resource}/date/{date}.json'
        return self._get_data(url=url)

    def _get_all_data(self, user_id: str, date: str):
        result = {
            'date': date
        }

        min_sedentary = self._get_activity_data(
            user_id, date, self._RESOURCE_MINUTES_SEDENTARY
        )
        result['minutesSedentary'] = _get_simple_value(min_sedentary, 'activities-tracker-minutesSedentary')

        min_lightly_active = self._get_activity_data(
            user_id, date, self._RESOURCE_MINUTES_LIGHTLY_ACTIVE
        )
        result['minutesLightlyActive'] = _get_simple_value(
            min_lightly_active, 'activities-tracker-minutesLightlyActive'
        )

        min_fairly_active = self._get_activity_data(
            user_id, date, self._RESOURCE_MINUTES_FAIRLY_ACTIVE
        )
        result['minutesFairlyActive'] = _get_simple_value(
            min_fairly_active, 'activities-tracker-minutesFairlyActive'
        )

        min_very_active = self._get_activity_data(
            user_id, date, self._RESOURCE_MINUTES_VERY_ACTIVE
        )
        result['minutesVeryActive'] = _get_simple_value(
            min_very_active, 'activities-tracker-minutesVeryActive'
        )

        min_activity_calories = self._get_activity_data(
            user_id, date, self._RESOURCE_ACTIVITY_CALORIES
        )
        result['activityCalories'] = _get_simple_value(
            min_activity_calories, 'activities-tracker-activityCalories'
        )

        sleep = self._get_sleep_data(
            user_id, date, self._RESOURCE_SLEEP
        )
        result['sleep'] = _get_sleep_value(sleep, 'summary')

        if self._flag_intraday:
            intra_calories = self._get_intra_day_activity_data(
                user_id, date, self._RESOURCE_CALORIES_INTRA
            )
            result['calories'] = _get_simple_value(intra_calories, 'activities-calories')
            result['calories-intraday'] = _get_intraday_value(intra_calories, 'activities-calories-intraday')

            intra_steps = self._get_intra_day_activity_data(
                user_id, date, self._RESOURCE_STEPS_INTRA
            )
            result['steps'] = _get_simple_value(intra_steps, 'activities-steps')
            result['steps-intraday'] = _get_intraday_value(intra_steps, 'activities-steps-intraday')

            intra_distance = self._get_intra_day_activity_data(
                user_id, date, self._RESOURCE_DISTANCE_INTRA
            )
            result['distance'] = _get_simple_value(intra_distance, 'activities-distance')
            result['distance-intraday'] = _get_intraday_value(intra_distance, 'activities-distance-intraday')

            intra_floors = self._get_intra_day_activity_data(
                user_id, date, self._RESOURCE_FLOORS_INTRA
            )
            result['floors'] = _get_simple_value(intra_floors, 'activities-floors')
            result['floors-intraday'] = _get_intraday_value(intra_floors, 'activities-floors-intraday')

            intra_elevation = self._get_intra_day_activity_data(
                user_id, date, self._RESOURCE_ELEVATION_INTRA
            )
            result['elevation'] = _get_simple_value(intra_elevation, 'activities-elevation')
            result['elevation-intraday'] = _get_intraday_value(intra_elevation, 'activities-elevation-intraday')

            intra_heart_rate = self._get_intra_day_heart_rate_data(
                user_id, date
            )
            result['heart'] = _get_simple_value(intra_heart_rate, 'activities-heart')
            result['heart-intraday'] = _get_intraday_value(intra_heart_rate, 'activities-heart-intraday')

        return result

    def _authorize(self):
        option = webdriver.ChromeOptions()
        option.add_argument("--incognito")
        option.add_argument("headless")
        print('start authorize')
        print(self._selenium_path)

        with webdriver.Chrome(self._selenium_path, options=option) as browser:
            print('start webdriver')
            browser.implicitly_wait(10)
            browser.get(self.auth_url)

            input_email = browser.find_element(By.CSS_SELECTOR, '#loginForm input[type="email"]')
            input_password = browser.find_element(By.CSS_SELECTOR, '#loginForm input[type="password"]')
            button_sign_in = browser.find_element(By.CSS_SELECTOR, '#loginForm button')

            input_email.send_keys(self._email)
            input_password.send_keys(self._password)
            button_sign_in.submit()

            _log(f'_authorize(): sign in with {self._email} / {self._password}')

            auth_code = _get_auth_code(
                browser=browser, callback=self._callback
            )
            _log(f'_authorize(): auth_code={auth_code}')

            self._update_auth_token(auth_code=auth_code)

    def retrieve(self, date: str):
        print('start retrieve')
        self._authorize()

        result = self._get_all_data(
            date=date,
            user_id=self._user_id
        )
        _log(f'retrieve(): Complete on {date}')

        return result
