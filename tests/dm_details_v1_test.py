import pytest
import requests
import json
import flask
from src import config

from src.other import clear_v1

# Fixture to reset data store
@pytest.fixture
def clear_server():
    requests.delete(config.url + 'clear/v1')
    pass

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
    
def test_invalid_token(clear_server, get_valid_token, get_valid_token_2):
    '''
    Tests case where token is invalid.

    Expects: 
        AccessError (403 error)
    '''

    user1 = get_valid_token
    user2 = get_valid_token_2
    invalid_token = '-10000'

    dm_id = requests.post(config.url + 'dm/create/v1', json={
        'token': user1['token'], 
        'u_ids': [user2['auth_user_id']]
    }).json()

    resp_details = requests.get(config.url + 'dm/details/v1', params={
        'token': invalid_token, 
        'dm_id': dm_id['dm_id']
        })
    assert resp_details.status_code == 403

def test_dm_details_v1_invalid_dm_id(clear_server, get_valid_token):
    '''
    Tests case where dm_id is invalid.

    Expects: 
        InputError (400 error)
    '''

    resp_details = requests.get(config.url + 'dm/details/v1', params={
        'token': get_valid_token['token'], 
        'dm_id': -1
        })
    assert resp_details.status_code == 400

def test_dm_details_v1_auth_user_not_member(clear_server, get_valid_token, get_valid_token_2):
    '''
    Tests case where auth_id is not a member of the dm.

    Expects: 
        AccessError (403 error)
    '''

    user1 = get_valid_token
    user2 = get_valid_token_2
    
    dm_id = requests.post(config.url + 'dm/create/v1', json={
        'token': user1['token'], 
        'u_ids': [user1['auth_user_id']]
        }).json()

    resp_details = requests.get(config.url + 'dm/details/v1', params={
        'token': user2['token'], 
        'dm_id': dm_id['dm_id']
        })
    assert resp_details.status_code == 403

def test_dm_details_v1_invalid_auth_user_and_dm_id(clear_server, get_valid_token):
    '''
    Tests returning access error as priority

    Expects: 
        AccessError (403 error)
    '''

    resp_details = requests.get(config.url + 'dm/details/v1', params={
        'token': 'asdasdasd', 
        'dm_id': -1
        })
    assert resp_details.status_code == 403

def test_dm_details_v1_returns_name(clear_server, get_valid_token, get_valid_token_2):
    '''
    Testing correct output.

    Expects: 
        Correct output from dm_details.
    '''

    user1 = get_valid_token
    user2 = get_valid_token_2

    dm_id = requests.post(config.url + 'dm/create/v1', json={
        'token': user1['token'], 
        'u_ids': [user2['auth_user_id']]
        }).json()

    resp_details = requests.get(config.url + 'dm/details/v1', params={
        'token': user1['token'], 
        'dm_id': dm_id['dm_id']
        }).json()

    assert resp_details['name'] == 'johnsmith, ownerone'

def test_dm_details_v1_returns_members(clear_server, get_valid_token, get_valid_token_2):
    '''
    Testing correct output.

    Expects: 
        Correct output from dm_details.
    '''
    
    user1 = get_valid_token
    user2 = get_valid_token_2

    dm_id = requests.post(config.url + 'dm/create/v1', json={
        'token': user1['token'], 
        'u_ids': [user2['auth_user_id']]
        }).json()

    resp_details = requests.get(config.url + 'dm/details/v1', params={
        'token': user1['token'], 
        'dm_id': dm_id['dm_id']
        }).json()

    print(resp_details['members'])
    assert resp_details['members'] == [
        {
            'u_id': user2['auth_user_id'],
            'email': 'owner@test.com',
            'name_first': 'owner',
            'name_last': 'one',
            'handle_str': 'ownerone'
        },
        {
            'u_id': user1['auth_user_id'],
            'email': 'example@email.com',
            'name_first': 'John',
            'name_last': 'smith',
            'handle_str': 'johnsmith'
        },
    ]
