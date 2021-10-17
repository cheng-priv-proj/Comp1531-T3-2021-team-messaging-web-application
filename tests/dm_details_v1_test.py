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
    

def test_invalid_token(clear_server, get_valid_token, get_valid_token_2):
    user1 = get_valid_token
    user2 = get_valid_token_2
    invalid_token = '-10000'

    dm_id = requests.post(config.url + 'dm/create/v1', json={
        'token': user1['token'], 
        'u_ids': [user2['auth_user_id']]
    }).json()

    resp_details = requests.get(config.url + 'dm/details/v1', json={
        'token': invalid_token, 
        'dm_id': dm_id['dm_id']
        })
    assert resp_details.status_code == 403

def test_dm_details_v1_invalid_dm_id(clear_server, get_valid_token):
    resp_details = requests.get(config.url + 'dm/details/v1', json={
        'token': get_valid_token, 
        'dm_id': -1
        })
    assert resp_details.status_code == 400

def test_dm_details_v1_auth_user_not_member(clear_server, get_valid_token, get_valid_token_2):
    user1 = get_valid_token
    user2 = get_valid_token_2
    
    dm_id = requests.post(config.url + 'dm/create/v1', json={
        'token': user1['token'], 
        'u_ids': [user2['auth_user_id']]
        }).json()

    resp_details = requests.get(config.url + 'dm/details/v1', json={
        'token': user1, 
        'dm_id': dm_id['dm_id']
        })
    assert resp_details.status_code == 403

def test_dm_details_v1_invalid_auth_user_and_dm_id(clear_server, get_valid_token):
    resp_details = requests.get(config.url + 'dm/details/v1', json={
        'token': get_valid_token, 
        'dm_id': -1
        })
    # should return access error as priority
    assert resp_details.status_code == 403

def test_dm_details_v1_returns_name(clear_server, get_valid_token, get_valid_token_2):
    user1 = get_valid_token
    user2 = get_valid_token_2

    dm_id = requests.post(config.url + 'dm/create/v1', json={
        'token': user1['token'], 
        'u_ids': [user2['auth_user_id']]
        }).json()

    resp_details = requests.get(config.url + 'dm/details/v1', json={
        'token': user1, 
        'dm_id': dm_id['dm_id']
        }).json()

    assert resp_details['name'] == 'Johnsmith, ownerone'

def test_dm_details_v1_returns_members(clear_server, get_valid_token, get_valid_token_2):
    user1 = get_valid_token
    user2 = get_valid_token_2

    dm_id = requests.post(config.url + 'dm/create/v1', json={
        'token': user1['token'], 
        'u_ids': [user2['auth_user_id']]
        }).json()

    resp_details = requests.get(config.url + 'dm/details/v1', json={
        'token': user1, 
        'dm_id': dm_id['dm_id']
        }).json()

    assert resp_details['members'] == [
        {
            'u_id': 1,
            'Email': 'example@email.com',
            'Name_first': 'John',
            'Name_last': 'smith',
            'Handle_str': 'Johnsmith'
        },
        {
            'u_id': 2,
            'Email': 'owner@test.com',
            'Name_first': 'owner',
            'Name_last': 'one',
            'Handle_str': 'ownerone'
        }
    ]
