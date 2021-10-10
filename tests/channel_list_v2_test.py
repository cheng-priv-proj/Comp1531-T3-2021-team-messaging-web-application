import pytest

from src.config import url
from src.other import clear_v1

import requests

# Clear_v2?
# Error code?

# Clears storage
@pytest.fixture
def clear():
    clear_v1()

# Generates the first user
@pytest.fixture
def first_register(extract_token, extract_channel):
    user_details = {
        'email': 'globalowner@test.com',
        'password': 'password', 
        'name_first': 'global',
        'name_last': 'user'
    }
    token_dict = requests.post(url + 'auth/register/v2', data = user_details).json()
    token = token_dict.get('token')

    channel_details = {
        'token': token,
        'name': 'channel',
        'is_public': True
    }
    channel_id_dict = requests.post(url + 'channels/create/v2', data = channel_details).json()
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
        token_dict = requests.post(url + 'auth/register/v2', data = user_details).json()
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
        channel_id_dict = requests.post(url + 'channels/create/v2', data = channel_details).json()
        channel_id = channel_id_dict.get('channel_id')

        return channel_id
    return register_channel_function


# Standard test for a valid input/output.
def test_channel_list_valid(clear, first_register, register_channel):
    token = first_register.get('token')
    channel_id1 = first_register.get('channel_id')

    channel_list = requests.get(url + 'channels/list/v2', params = {token}).json()

    assert channel_list == { 
        'channels': [
            {
                'channel_id': channel_id1, 
                'name': 'channel'
            }
        ]
    }

    channel_id2 = register_channel(token, 'channel2', True)
    channel_list = requests.get(url + 'channels/list/v2', params = {token}).json()

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
        ]
    }

# Testing for an empty list of channels.
def test_channel_list_nochannels(clear, register_user):
    no_server_token = register_user('noserver@test.com')
    channel_list = requests.get(url + 'channels/list/v2', params = {no_server_token}).json()

    assert channel_list == { 
        'channels': [

        ]
    }

# Testing if the function returns any channels the user is not part of.
def test_channel_list_other_owners_test(clear, first_register, register_user, register_channel):
    token1 = first_register.get('token')
    channel_id1 = first_register.get('channel_id')

    token2 = register_user('owner2@test.com')
    channel_id2 = register_channel(token2, 'channel2', True)

    channel_list1 = requests.get(url + 'channels/list/v2', params = {token1}).json()
    channel_list2 = requests.get(url + 'channels/list/v2', params = {token2}).json()

    assert channel_list1 == { 
        'channels': [
            {
                'channel_id': channel_id1, 
                'name': 'channel'
            }
        ]
    }

    assert channel_list2 == { 
        'channels': [
            {
                'channel_id': channel_id2, 
                'name': 'channel2'
            }
        ]
    }

# Tests the case that a user joins a new channel, and looking for an update the the list.
def test_channel_list_after_newjoin_test(clear, first_register, register_user):
    channel_id = first_register.get('channel_id')
    token2 = register_user('user2@test.com')

    requests.post(url + 'channel/join/v2', data = {token2, channel_id})

    channel_list = requests.get(url + 'channels/list/v2', params = {token2}).json()
    assert channel_list == { 
        'channels': [
            {
                'channel_id': channel_id, 
                'name': 'channel'
            }
        ]
    }

# Tests whether the auth id is invalid.
def test_invalid_auth_id(clear):
    invalid_token = 1000
    
    invalid_request = requests.get(url + 'channels/list/v2', params = {invalid_token})
    assert (invalid_request.status_code) == 400



## Ignore this
# # Generates a number of tokens given a number
# @pytest.fixture
# def token_factory():
#     def token_factory_function(token_quantity):
#         tokens = []
#         for i in range(0, token_quantity):
#             register_details = {
#                 'email': 'user' + str(i) + '@test.com',
#                 'password': 'password', 
#                 'name_first': 'user' + str(i), 
#                 'name_last': 'user'
#             }
#             registered = requests.get(url + 'auth/register/v2', params = register_details)
#             tokens.append(registered['tokens'])
#         return tokens
#     return token_factory_function

# # Generates a number of channels given a list of tokens
# def channel_factory():
#     def channel_factory_function(token_list):
#         for token in token_list:
#             channel_id_list = []
#             register_details = {
#                 'token': token,
#                 'name': 'channel' + str(token),
#                 'is_public': True
#             }

#             created = requests.get(url + 'channels/create/v2', params = register_details)
#             channel_id_list.append(created['channel_id'])
#         return channel_id_list
#     return channel_factory_function