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
def second_register():
    user_details = {
        'email': 'globalowner2@test.com',
        'password': 'password', 
        'name_first': 'global2',
        'name_last': 'user'
    }
    token_dict = requests.post(url + 'auth/register/v2', json = user_details).json()
    token = token_dict.get('token')

    channel_details = {
        'token': token,
        'name': 'channel2',
        'is_public': True
    }
    channel_id_dict = requests.post(url + 'channels/create/v2', json = channel_details).json()
    channel_id = channel_id_dict.get('channel_id')

    auth_user_id = token_dict.get('auth_user_id')
    
    return {'token': token, 'auth_user_id': auth_user_id, 'channel_id': int(channel_id)}

# Test input u_id does not refer to valid
def test_invalid_u_id(clear, first_register):
    token = first_register.get('token')
    invalid_u_id = -10000
    permission_id = 1

    assert requests.post(url + 'admin/userpermission/change/v1', json = {
        'token': token, 
        'u_id': invalid_u_id,
        'permission_id': permission_id
    }).status_code == 400

# Test input permission id is invalid
def test_invalid_permission_id(clear, first_register, second_register):
    token = first_register.get('token')
    u_id = second_register.get('auth_user_id')
    invalid_permission_id = 3

    assert requests.post(url + 'admin/userpermission/change/v1', json = {
        'token': token, 
        'u_id': u_id,
        'permission_id': invalid_permission_id
    }).status_code == 400

# Test u_id is the only global owner and demote to user
def test_demote_only_owner(clear, first_register):
    token = first_register.get('token')
    u_id = first_register.get('auth_user_id')
    permission_id = 2

    assert requests.post(url + 'admin/userpermission/change/v1', json = {
        'token': token, 
        'u_id': u_id,
        'permission_id': permission_id
    }).status_code == 400

# Test successful perms change
def test_success_perms_change(clear, first_register, second_register):
    first_token = first_register.get('token')
    first_u_id = first_register.get('auth_user_id')

    second_token = second_register.get('token')
    second_u_id = second_register.get('auth_user_id')
    
    become_owner = 1
    become_member = 2

    # Makes second user an owner
    assert requests.post(url + 'admin/userpermission/change/v1', json = {
        'token': first_token, 
        'u_id': second_u_id,
        'permission_id': become_owner
    }).status_code == 200

    # Makes first user member
    assert requests.post(url + 'admin/userpermission/change/v1', json = {
        'token': second_token, 
        'u_id': first_u_id,
        'permission_id': become_member
    }).status_code == 200

    # Tries to change second as user
    assert requests.post(url + 'admin/userpermission/change/v1', json = {
        'token': second_token, 
        'u_id': second_u_id,
        'permission_id': become_member
    }).status_code == 400

# Access if not global owner
def test_no_perms(clear, first_register, second_register):
    first_u_id = first_register.get('auth_user_id')

    second_token = second_register.get('token')

    become_member = 2

    # Makes first user member
    assert requests.post(url + 'admin/userpermission/change/v1', json = {
        'token': second_token, 
        'u_id': first_u_id,
        'permission_id': become_member
    }).status_code == 403

# Access if not valid token
def test_not_valid_token(clear, first_register, second_register):
    invalid_token = '-10000'
    u_id = second_register.get('auth_user_id')
    permission_id = 1

    assert requests.post(url + 'admin/userpermission/change/v1', json = {
        'token': invalid_token, 
        'u_id': u_id,
        'permission_id': permission_id
    }).status_code == 403

