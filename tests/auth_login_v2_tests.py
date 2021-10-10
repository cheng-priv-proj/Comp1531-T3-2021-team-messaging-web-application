import pytest
import requests
import json
import flask
from src import config

import pytest

from src.auth import *
from src.error import InputError
from src.other import clear_v2
from src.other import clear_v1

# clear_v2

# Fixture to reset data store before every test
@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def clear_server():
    clear_v2()

# Extracts the auth_user_id from a given dictionary.
@pytest.fixture
def extract_user_v2():
    def extract_user_id_function(auth_user_id_dict):
        return auth_user_id_dict['auth_user_id']
    return extract_user_id_function

@pytest.fixture
def extract_user_v2_token():
    def extract_user_id_token(auth_user_id_dict):
        return auth_user_id_dict['token']
    return extract_user_id_token

# Fixture that registers a valid user.
@pytest.fixture
def auth_id_v2(clear_server):
    response = requests.post(config.url + 'auth/register/v2', data={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    return response.json()


def test_standard_v2(auth_id_v2, extract_user_v2):

    requests.post(config.url + 'auth/login/v2', data={'email': 'example@email.com', 'password': 'potato'}).json()
    dict_id_token = requests.get(config.url + 'auth/login/v2', params={'email': 'example@email.com', 'password': 'potato'}).json()
    dict_id_token_register = (requests.get(config.url + 'auth/register/v2', params={'email': 'example@email.com', 'password': 'potato', 'name_first': 'John', 'name_last' : 'smith'})).json()
    
    assert extract_user_v2(dict_id_token) == extract_user_v2(dict_id_token_register), 'Valid case: Auth_id not successful'

def test_incorrect_password_v2(auth_id_v2):
    resp = requests.post(config.url + 'auth/login/v2', data={'email': 'example@email.com', 'password': 'rongPASSWORD'})
    assert(resp.status_code == 400)


# Test that expects an input error when given a non-existant email.
def test_email_does_not_exist_v2(auth_id_v2):
    resp = requests.post(config.url + 'auth/login/v2', data={'email': 'baaaaddexample@email.com', 'password': 'potato'})
    assert(resp.status_code == 400)

# Test that expects an input error when all the fields are invalid. 
def test_all_incorrect_v2(clear, auth_id):
    with pytest.raises(InputError):
        auth_login_v1("invalid@gmail.com", "notpotato")

def test_invalid_return_token_v2():
    return