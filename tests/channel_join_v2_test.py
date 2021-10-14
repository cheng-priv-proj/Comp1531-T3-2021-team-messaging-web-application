import pytest

from src.config import url
from src.other import clear_v1

import requests

# Clears storage
@pytest.fixture
def clear():
    requests.delete(url + "clear/v1")


# Generates the first user
@pytest.fixture
def first_register():
    user_details = {
        'email': 'globalowner@test.com',
        'password': 'password', 
        'name_first': 'global',
        'name_last': 'user'
    }
    token_dict = requests.post(url + 'auth/register/v2', json = user_details).json()
    print(token_dict)
    token = token_dict.get('token')

    channel_details = {
        'token': token,
        'name': 'channel',
        'is_public': True
    }
    channel_id_dict = requests.post(url + 'channels/create/v2', json = channel_details).json()
    channel_id = channel_id_dict.get('channel_id')
    
    return {'token': token, 'channel_id': channel_id}

# Creates a user using the given details and returns the channel_id
@pytest.fixture 
def register_user():
    def register_user_function(email):
        user_details = {
            'email': email,
            'password': 'password', 
            'name_first': 'some',
            'name_last': 'user'
        }
        token_dict = requests.post(url + 'auth/register/v2', json = user_details).json()
        token = token_dict.get('token')

        return token
    return register_user_function

# Creates a channel using the given details and returns the channel_id
@pytest.fixture
def register_channel():
    def register_channel_function(token, name, is_public):
        channel_details = {
            'token': token,
            'name': name,
            'is_public': is_public
        }
        channel_id_dict = requests.post(url + 'channels/create/v2', json = channel_details).json()
        channel_id = channel_id_dict.get('channel_id')

        return channel_id
    return register_channel_function

def test_valid_id(clear, first_register, register_user):
    token2 = register_user('member2@test.com')
    channel_id = first_register.get('channel_id')
    print(token2, channel_id)
    r = requests.post(url + 'channel/join/v2', json = {'token': token2,'channel_id': channel_id})
    print(r)
    channel_list = requests.get(url + 'channels/list/v2', json = {'token': token2}).json()
    print("channel list:   ", channel_list)
    assert channel_list == {
        'channels': [
        	{
                'channel_id': channel_id, 
                'name': 'channel'
            }
        ],
    }

def test_multiple_servers(clear, first_register, register_user, register_channel):
    channel_id1 = first_register.get('channel_id')

    owner_token2 = register_user('owner2@test.com')
    channel_id2 = register_channel(owner_token2, 'channel2', True) 

    member_token = register_user('member@test.com')
    
    requests.post(url + 'channel/join/v2', json = {'token': member_token, 'channel_id': channel_id1})
    requests.post(url + 'channel/join/v2', json = {'token': member_token, 'channel_id': channel_id2})

    channel_list = requests.get(url + 'channels/list/v2', json = {"token": member_token}).json()

    assert channel_list == {
        'channels': [
        	{
                'channel_id': channel_id1, 
                'name': 'channel'
            },
            {
                'channel_id': channel_id2, 
                'name': 'channel2'
            }
        ],
    }

def test_invalid_channel_id(clear, first_register):
    token = first_register.get('token')
    invalid_channel_id = 10000

    invalid_request = requests.post(url + 'channel/join/v2', json = {'token': token, "channel_id": invalid_channel_id})
    assert (invalid_request.status_code) == 400

def test_invalid_user_id(clear, first_register):
    invalid_token = 10000
    channel_id = first_register.get('channel_id')

    invalid_request = requests.post(url + 'channel/join/v2', json = {'token': invalid_token, "channel_id": channel_id})
    assert (invalid_request.status_code) == 403

# Test expecting prority to AccessError when an invalid auth_id and channel_id are given.
def test_invalid_user_id_and_invalid_channel_id(clear):
    invalid_token = 10000
    invalid_channel_id = 10000

    invalid_request = requests.post(url + 'channel/join/v2', json = {'token': invalid_token, "channel_id": invalid_channel_id})
    assert (invalid_request.status_code) == 403

def test_already_member(clear, first_register, register_user, register_channel):
    member_token = register_user('member@test.com')
    channel_id = first_register.get('channel_id')

    requests.post(url + 'channel/join/v2', json = {'token': member_token, "channel_id": channel_id})

    invalid_request = requests.post(url + 'channel/join/v2', json = {'token': member_token, "channel_id": channel_id})
    assert (invalid_request.status_code) == 400

def test_already_owner(clear, first_register):
    token = first_register.get('token')
    channel_id = first_register.get('channel_id')

    invalid_request = requests.post(url + 'channel/join/v2', json = {'token': token, "channel_id": channel_id})
    assert (invalid_request.status_code) == 400

def test_private_not_owner(clear, register_user, register_channel):
    owner_token2 = register_user('owner2@test.com')
    private_channel_id = register_channel(owner_token2, 'channel2', False)

    member_token = register_user('member@test.com')
    
    invalid_request = requests.post(url + 'channel/join/v2', json = {'token': member_token, "channel_id": private_channel_id})
    assert (invalid_request.status_code) == 403

# Testing that global owner has the correct permissions.
def test_global_owner(clear, register_user, register_channel):
    global_owner_token = register_user('owner2@test.com')

    owner_token = register_user('member@test.com')
    member_token = register_user('member2@test.com')

    private_channel_id = register_channel(owner_token, 'channel', False)

    requests.post(url + 'channel/join/v2', json = {'token': global_owner_token, "channel_id": private_channel_id})
    channel_list = requests.get(url + 'channels/list/v2', json = {'token': global_owner_token}).json()

    assert channel_list == { 
        'channels': [
            {
                'channel_id': private_channel_id, 
                'name': 'channel'
            }
        ]
    }

    invalid_request = requests.post(url + 'channel/join/v2', json = {'token': member_token, "channel_id": private_channel_id})
    assert (invalid_request.status_code) == 403
