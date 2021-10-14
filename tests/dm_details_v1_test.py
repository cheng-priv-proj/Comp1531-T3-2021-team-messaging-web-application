import pytest
import requests
import json
import flask
from src import config

from src.other import clear_v1

# Fixture to reset data store
@pytest.fixture
def clear_server():
    #clear_v2()
    pass

@pytest.fixture
def get_valid_token(clear_server):
    response = requests.post(config.url + 'auth/register/v2', data={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    token = response.json()
    return token['token']

@pytest.fixture
def get_valid_token_2():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'owner@test.com', 
        'password': 'spotato', 
        'name_first': 'owner', 
        'name_last' : 'one'
    })
    return response.json()

@pytest.fixture
def get_dm_id(get_valid_token, get_valid_token_2):
    resp = requests.post(config.url + 'dm/create/v1', json={'token': get_valid_token['token'], 'u_ids': [get_valid_token_2['auth_user_id']]}).json()
    return resp['dm_id']


def test_dm_details_v1_invalid_dm_id(clear_server):
    resp_details = requests.get(config.url + 'dm/details/v1', json={'token': get_valid_token, 'dm_id': -1}).json()
    assert resp_details.status_code == 400

def test_dm_details_v1_auth_user_not_member(clear_server):
    resp_details = requests.get(config.url + 'dm/details/v1', json={'token': get_valid_token, 'dm_id': get_dm_id}).json()
    assert resp_details.status_code == 403

def test_dm_details_v1_returns_name(clear_server):
    resp_details = requests.get(config.url + 'dm/details/v1', json={'token': get_valid_token, 'dm_id': get_dm_id}).json()
    assert resp_details['name'] == ['Johnsmith', 'ownerone']

def test_dm_details_v1_returns_members(clear_server):
    resp_details = requests.get(config.url + 'dm/details/v1', json={'token': get_valid_token, 'dm_id': get_dm_id}).json()

    #not sure what members looks like
    assert resp_details['members'] == ''
