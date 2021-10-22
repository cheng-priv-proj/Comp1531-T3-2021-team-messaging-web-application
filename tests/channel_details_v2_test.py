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
    token = token_dict.get('token')

    channel_details = {
        'token': token,
        'name': 'channel',
        'is_public': True
    }
    channel_id_dict = requests.post(url + 'channels/create/v2', json = channel_details).json()
    channel_id = channel_id_dict.get('channel_id')
    
    return {'token': token, 'channel_id': channel_id, 'auth_user_id': token_dict.get('auth_user_id')}

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

# Test expecting AccessError when given a valid Auth_id that is not in the channel.
def test_user_with_no_access_to_channel(clear, first_register, register_user):
    invalid_token = register_user('user2@test.com')
    channel_id = first_register.get('channel_id')

    invalid_request = requests.get(url + 'channel/details/v2', params = {'token': invalid_token, 'channel_id': channel_id})
    assert (invalid_request.status_code) == 403



def test_invalid_channel_id(clear, first_register):
    token = first_register.get('token')
    invalid_channel_id = 10000

    invalid_request = requests.get(url + 'channel/details/v2', params = {'token': token, 'channel_id': invalid_channel_id})
    assert (invalid_request.status_code) == 400

def test_invalid_auth_id(clear, first_register):
    invalid_token = 10000
    channel_id = first_register.get('channel_id')

    invalid_request = requests.get(url + 'channel/details/v2', params = {'token': invalid_token, "channel_id": channel_id})
    assert (invalid_request.status_code) == 403

def test_returns_all_info(clear, first_register):
    token = first_register.get('token')
    channel_id = first_register.get('channel_id')

    channel_details = requests.get(url + 'channel/details/v2', params = {'token': token, "channel_id": channel_id}).json()

    assert channel_details == {
        'name': 'channel',
        'is_public': True,
        'owner_members': [
            {
                'u_id': first_register.get('auth_user_id'),
                'email': 'globalowner@test.com',
                'name_first': 'global',
                'name_last': 'user',
                'handle_str': 'globaluser'
            }
        ],
        'all_members': [
            {
                'u_id': first_register.get('auth_user_id'),
                'email': 'globalowner@test.com',
                'name_first': 'global',
                'name_last': 'user',
                'handle_str': 'globaluser'
            }
        ]
    }