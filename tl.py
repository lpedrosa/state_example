import time
import urllib
from dataclasses import dataclass

import requests


def generate_auth_link(client_id, redirect_uri, state):
    query = urllib.parse.urlencode({
        'response_type': 'code',
        'response_mode': 'form_post',
        'client_id': client_id,
        # hardcoded the scopes
        'scope': 'accounts balance offline_access',
        'nonce': int(time.time()),
        'redirect_uri': redirect_uri,
        'state': state,
        'enable_mock': 'true',
    })

    return f'https://auth.truelayer.com/?{query}'


@dataclass
class Tokens:
    access: str
    refresh: str


def exchange_code(code, client_id, client_secret, redirect_uri):
    body = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
    }
    res = requests.post('https://auth.truelayer.com/connect/token', data=body)
    res.raise_for_status()

    token_json = res.json()

    return Tokens(access=token_json['access_token'],
                  refresh=token_json['refresh_token'])


def list_accounts(token):
    auth_header = {'Authorization': f'Bearer {token}'}

    res = requests.get('https://api.truelayer.com/data/v1/accounts',
                       headers=auth_header)
    res.raise_for_status()

    api_result = res.json()

    return api_result['results']


def token_info(token):
    auth_header = {'Authorization': f'Bearer {token}'}

    res = requests.get('https://api.truelayer.com/data/v1/me',
                       headers=auth_header)
    res.raise_for_status()

    api_result = res.json()['results'][0]

    return api_result
