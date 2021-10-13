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

# Fixture to register someone and returns a dictionary of {token, auth_user_id}
@pytest.fixture
def get_valid_token():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
    })
    return response.json()

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
def get_valid_token_3():
    response = requests.post(config.url + 'auth/register/v2', json={
            'email': 'eexample@email.com',
            'password': 'spotatoo', 
            'name_first': 'Johno',
            'name_last': 'smith',
    })
    return response.json()


def test_dm_create_v1_invalid_u_id(clear_server, get_valid_token):
    invalid_auth_ids = ['a', 'b', '-1']
    resp = requests.post(config.url + 'dm/create/v1', json={'token': get_valid_token['token'], 'u_ids': invalid_auth_ids}).json()
    
    assert resp.status_code == 400

# assumption: dm_ids are generated based on how many already exist
def test_dm_create_v1_returns_id(clear_server, get_valid_token, get_valid_token_2, get_valid_token_3):
    auth_ids = [get_valid_token['auth_user_id'], get_valid_token_2['auth_user_id']]
    resp = requests.post(config.url + 'dm/create/v1', json={'token': get_valid_token_3['token'], 'u_ids': auth_ids}).json()

    assert resp['dm_id'] == 1

def test_dm_create_v1_returns_unique_ids(clear_server, get_valid_token, get_valid_token_2, get_valid_token_3):
    user1 = get_valid_token['auth_user_id']
    user2 = get_valid_token_2['auth_user_id']
    user3 = get_valid_token_3['auth_user_id']
    
    resp1 = requests.post(config.url + 'dm/create/v1', json={'token': user1['token'], 'u_ids': [user2, user3]}).json()
    resp2 = requests.post(config.url + 'dm/create/v1', json={'token': user3['token'], 'u_ids': [user1, user2]}).json()

    assert resp1['dm_id'] != resp2['dm_id']

def test_dm_create_v1_name(clear_server, get_valid_token, get_valid_token_2, get_valid_token_3):
    auth_ids = [get_valid_token['auth_user_id'], get_valid_token_2['auth_user_id']]

    resp = requests.post(config.url + 'dm/create/v1', json={'token': get_valid_token_3['token'], 'u_ids': auth_ids}).json()
    resp_details = requests.get(config.url + 'dm/details/v1', json={'token': get_valid_token_3, 'dm_id': resp['dm_id']}).json()

    assert resp_details['name'] == ['Johnsmith', 'ownerone']

def test_dm_create_v1_members(clear_server, get_valid_token, get_valid_token_2, get_valid_token_3):
    auth_ids = [get_valid_token['auth_user_id'], get_valid_token_2['auth_user_id']]
    resp = requests.post(config.url + 'dm/create/v1', json={'token': get_valid_token_3['token'], 'u_ids': auth_ids}).json()
    resp_details = requests.get(config.url + 'dm/details/v1', json={'token': get_valid_token_3, 'dm_id': resp['dm_id']}).json()

    #not sure what members looks like
    assert resp_details['members'] == ''
