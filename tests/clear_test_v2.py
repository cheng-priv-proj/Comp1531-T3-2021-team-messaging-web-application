import pytest

import requests
from src.config import url

from os import path

def test_clear():
    direct = 'src/json_dump/data_store.json'
    empty_json = path.getsize(direct)

    user_details = {
        'email': 'globalowner@test.com',
        'password': 'password', 
        'name_first': 'global',
        'name_last': 'user'
    }
    token_dict = requests.post(url + 'auth/register/v2', json = user_details).json()

    assert empty_json != path.getsize(direct)

    requests.delete(url + 'clear/v1', params = {})

    assert empty_json == path.getsize(direct)