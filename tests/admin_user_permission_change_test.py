import pytest

from src.config import url
from src.other import clear_v1

import requests

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

    auth_user_id = token_dict.get('auth_user_id')
    
    return {'token': token, 'auth_user_id': auth_user_id, 'channel_id': int(channel_id)}

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

        return token_dict
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

def test_invalid_u_id(clear, first_register):
    token = first_register.get('token')
    invalid_u_id = -10000
    permission_id = 1

    assert requests.get(url + 'admin/userpermission/change/v1', json = {
        'token': token, 
        'u_id': invalid_u_id,
        'permission_id': permission_id
    }).status_code == 400

def test_invalid_permission_id(clear, first_register, register_user):
    token = first_register.get('token')




# Test input u_id does not refer to valid
# Test input permission id is invalid
# Test u_id is the only global owner and demote to user
# Access if not global owner
# Access if not valid token
# admin/userpermission/change/v1
# 1 is owner
# 2 is user 