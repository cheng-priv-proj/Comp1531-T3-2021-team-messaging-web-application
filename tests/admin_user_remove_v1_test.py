import json
from _pytest.python_api import approx
import pytest
import requests
from datetime import date, datetime

from src.config import url

@pytest.fixture
def clear():
    requests.delete(url + 'clear/v1')

@pytest.fixture
def register(clear):
    owner_info = requests.post(url + 'auth/register/v2', json={
        'email': 'owner@email.com',
        'password': 'password',
        'name_first': 'owner',
        'name_last': 'one'
    }).json()

    user_info = requests.post(url + 'auth/register/v2', json={
        'email': 'user@email.com',
        'password': 'password',
        'name_first': 'user',
        'name_last': 'one'
    }).json()
    
    return [owner_info, user_info]

def test_standard(register):
    '''
    A test for the standard valid case 

    Expects: 
        Successful removal (status code 200)

    '''

    channel_now = datetime.utcnow().timestamp()

    channel_id_dict = requests.post(url + 'channels/create/v2', json={
        'token': register[1].get('token'),
        'name': 'channel',
        'is_public': True
    }).json()

    requests.post(url + 'channel/join/v2', json = {
        'token': register[0].get('token'), 
        'channel_id': channel_id_dict.get('channel_id')
    })

    dm_now = datetime.utcnow().timestamp()
    
    channel_message = requests.post(url + 'message/send/v1', json={
        'token': register[1].get('token'),
        'channel_id': channel_id_dict.get('channel_id'),
        'message': 'message of a deleted person'
    }).json()

    dm_id_dict = requests.post(url + 'dm/create/v1', json={
        'token': register[1].get('token'),
        'u_ids': [register[0].get('auth_user_id')]
    }).json()

    dm_message = requests.post(url + 'message/senddm/v1', json={
        'token': register[1].get('token'),
        'dm_id': dm_id_dict.get('dm_id'),
        'message': 'message of another deleted person'
    }).json()

    requests.delete(url + 'admin/user/remove/v1', json={
        'token': register[0].get('token'),
        'u_id': register[1].get('auth_user_id')
    })

    # check if user info has been correctly overwritten
    assert requests.get(url + 'user/profile/v1', params = {
        'token': register[0].get('token'),
        'u_id': register[1].get('auth_user_id')
    }).json().get('user') == {
        'u_id': register[1].get('auth_user_id'),
        'email': '',
        'name_first': 'Removed',
        'name_last': 'user',
        'handle_str': ''
    }

    # check if channel message has been overwritten
    assert requests.get(url + 'channel/messages/v2', params = {
        'token': register[0].get('token'),
        'channel_id': channel_id_dict.get('channel_id'),
        'start': 0
    }).json() == {
        'start': 0,
        'end': -1,
        'messages': [{
            'u_id': register[1].get('auth_user_id'),
            'message': 'Removed user',
            'time_created': pytest.approx(channel_now, rel = 5),
            'message_id': channel_message.get('message_id')
        }]
    }

    # check if dm message has been overwritten
    assert requests.get(url + 'dm/messages/v1', params = {
        'token': register[0].get('token'),
        'dm_id': dm_id_dict.get('dm_id'),
        'start': 0
    }).json() == {
        'start': 0,
        'end': -1,
        'messages': [{
            'u_id': register[1].get('auth_user_id'),
            'message': 'Removed user',
            'time_created': pytest.approx(dm_now, rel = 5),
            'message_id': dm_message.get('message_id')
        }]
    }

    # check if user appears in user/all 
    assert requests.get(url + 'users/all/v1', params = {
        'token': register[0].get('token')
    }).json() == {
        'users': [{
            'u_id': register[0].get('auth_user_id'),
            'email': 'owner@email.com',
            'name_first': 'owner',
            'name_last': 'one',
            'handle_str': 'ownerone'
        }]
    }

    # check if handle and email can be reused
    new_user = requests.post(url + 'auth/register/v2', json={
        'email': 'user@email.com',
        'password': 'password',
        'name_first': 'user',
        'name_last': 'one'
    }).json()

    assert requests.get(url + 'user/profile/v1', params = {
        'token': register[0].get('token'),
        'u_id': new_user.get('auth_user_id')
    }).json().get('user') == {
        'u_id': new_user.get('auth_user_id'),
        'email': 'user@email.com',
        'name_first': 'user',
        'name_last': 'one',
        'handle_str': 'userone'
    }

def test_invalid_u_id(register):
    '''
    Test that expects input error when given an invalid u_id

    Expects: 
        InputError (400 error) 
    '''

    assert requests.delete(url + 'admin/user/remove/v1', json={
        'token': register[0].get('token'),
        'u_id': 123123
    }).status_code == 400

def test_only_global_owner(register):
    '''
    Test that expects input error when there is only one global owner

    Expects: 
        InputError (400 error) 
    '''

    assert requests.delete(url + 'admin/user/remove/v1', json={
        'token': register[0].get('token'),
        'u_id': register[0].get('auth_user_id')
    }).status_code == 400

    assert requests.post(url + 'admin/userpermission/change/v1', json={
        'token': register[0].get('token'),
        'u_id': register[1].get('auth_user_id'),
        'permission_id': 1
    }).status_code == 200

    assert requests.delete(url + 'admin/user/remove/v1', json={
        'token': register[0].get('token'),
        'u_id': register[0].get('auth_user_id')
    }).status_code == 200

    assert requests.delete(url + 'admin/user/remove/v1', json={
        'token': register[1].get('token'),
        'u_id': register[1].get('auth_user_id')
    }).status_code == 400

def test_auth_user_not_global_owner(register):
    '''
    Test that expects an Access error when the given auth_id is not a global owner.

    Expects: 
        AccessError (403 error) 
    '''

    assert requests.delete(url + 'admin/user/remove/v1', json={
        'token': register[1].get('token'),
        'u_id': register[1].get('auth_user_id')
    }).status_code == 403

def test_token_invalid(register):
    '''
    Test that expects Access error when given an invalid token.

    Expects: 
        AccessError (403 error) 
    '''

    assert requests.delete(url + 'admin/user/remove/v1', json={
        'token': 'not a real token',
        'u_id': register[0].get('auth_user_id')
    }).status_code == 403


def test_invalid_u_id_and_token(clear):
    '''
    Test that expects that Access error takes precedence when both u_id and token are invalid.

    Expects: 
        AccessError (403 error) 
    '''
    
    assert requests.delete(url + 'admin/user/remove/v1', json={
        'token': 'not a real token',
        'u_id': 123123
    }).status_code == 403