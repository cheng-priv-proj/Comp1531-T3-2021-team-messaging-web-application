import pytest
import requests
import json
import flask
from src import config

import pytest
from src.other import clear_v1

# Clears the datastore.
@pytest.fixture
def clear():
    requests.delete(config.url + "clear/v1")

# Generates new user
@pytest.fixture
def get_valid_token():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
    })
    return response.json()
    
# Generates the first user
@pytest.fixture
def first_register():
    user_details = {
        'email': 'globalowner@test.com',
        'password': 'password', 
        'name_first': 'global',
        'name_last': 'user'
    }
    token_dict = requests.post(config.url + 'auth/register/v2', json = user_details).json()
    token = token_dict.get('token')
    u_id = token_dict.get('auth_user_id')

    channel_details = {
        'token': token,
        'name': 'channel',
        'is_public': True
    }
    channel_id_dict = requests.post(config.url + 'channels/create/v2', json = channel_details).json()
    channel_id = channel_id_dict.get('channel_id')
    
    return {'u_id': u_id, 'token': token, 'channel_id': channel_id}


def test_channel_removeowner_v1_invalid_token(clear, first_register, get_valid_token):
    '''
    Tests case where the given token is invalid. 

    Expects: 
        AccessError (403 error)
    '''

    details = first_register
    new_user = get_valid_token
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': -1,
        'channel_id': details['channel_id'],
        'u_id': new_user['auth_user_id']
    })

    assert resp.status_code == 403

def test_channel_removeowner_v1_invalid_channel_id(clear, first_register, get_valid_token):
    '''
    Tests case where channel_id is invalid.

    Expects: 
        InputError (400 error)
    '''

    details = first_register
    new_user = get_valid_token
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': details['token'], 
        'channel_id': -1, 
        'u_id': new_user['auth_user_id']
    })

    assert resp.status_code == 400


def test_channel_removeowner_v1_invalid_token_and_channel_id(clear, get_valid_token):
    '''
    Test ensuring access error has priority when token and channel_id are invalid. 

    Expects: 
        AccessError (403 error)
    '''
    new_user = get_valid_token
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': -1, 
        'channel_id': -1, 
        'u_id': new_user['auth_user_id']
    })

    assert resp.status_code == 403

def test_channel_removeowner_v1_invalid_u_id(clear, first_register):
    '''
    Tests case where u_id is invalid.

    Expects: 
        InputError (400 error)
    '''

    details = first_register
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': details['token'], 
        'channel_id': details['channel_id'], 
        'u_id': -1})

    assert resp.status_code == 400

def test_channel_removeowner_v1_user_not_member_of_channel(clear, first_register, get_valid_token):
    '''
    Tests case where the user is not a member of the channel.

    Expects: 
        InputError (400 error)
    '''

    details = first_register
    new_user = get_valid_token
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': details['token'], 
        'channel_id': details['channel_id'], 
        'u_id': new_user['auth_user_id']})

    assert resp.status_code == 400

def test_channel_removeowner_v1_user_only_owner_of_channel(clear, first_register):
    '''
    Tests case where channel_id is invalid.

    Expects: 
        InputError (400 error)
    '''

    details = first_register
    requests.post(config.url + 'channel/join/v2', json={
        'token': details['token'], 
        'channel_id': details['channel_id']
    })
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': details['token'], 
        'channel_id': details['channel_id'], 
        'u_id': details['u_id']
    })
    
    assert resp.status_code == 400
    
def test_channel_removeowner_v1_user_without_owner_permissions(clear, first_register, get_valid_token):
    '''
    Tests case where the user does not have the correct perms.

    Expects: 
        AccessError (403 error)
    '''

    details = first_register
    new_user = get_valid_token
    requests.post(config.url + 'channel/join/v2', json={
        'token': details['token'], 
        'channel_id': details['channel_id']
    })

    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': new_user['token'], 
        'channel_id': details['channel_id'], 
        'u_id': new_user['auth_user_id']
    })

    assert resp.status_code == 403

def test_channel_removeowner_v1_works(clear, first_register, get_valid_token):
    '''
    Testing standard valid case.

    Expects: 
        Correct output from channel/details.
    '''
    details = first_register
    new_user = get_valid_token
    requests.post(config.url + 'channel/join/v2', json={
        'token': new_user['token'], 
        'channel_id': details['channel_id']
    })

    assert requests.post(config.url + 'channel/addowner/v1', json={
        'token': details['token'], 
        'channel_id': details['channel_id'], 
        'u_id': new_user['auth_user_id']
    }).status_code == 200

    assert requests.post(config.url + 'channel/removeowner/v1', json={
        'token': details['token'], 
        'channel_id': details['channel_id'], 
        'u_id': new_user['auth_user_id']
    }).status_code == 200

    channel_details = requests.get(config.url + 'channel/details/v2', params={
        'token': new_user['token'], 
        'channel_id': details['channel_id']
    }).json()

    assert new_user['auth_user_id'] not in [user['u_id'] for user in channel_details['owner_members']]
    # checking user still in channel
    assert new_user['auth_user_id'] in [user['u_id'] for user in channel_details['all_members']]
