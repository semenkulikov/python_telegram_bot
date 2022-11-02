import requests


def request_to_api(url, headers, querystring):
    try:
        response = requests.get(url=url, headers=headers, params=querystring, timeout=10)
        if response.status_code == requests.codes.ok:
            return response
    except (ConnectionError, ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError):
        raise ValueError('Ошибка! Какие-то проблемы с интернетом!')
