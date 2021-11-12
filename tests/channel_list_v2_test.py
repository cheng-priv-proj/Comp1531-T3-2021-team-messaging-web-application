import pytest

from src.config import url
from src.other import clear_v1

import requests

@pytest.fixture
def clear():
    '''
    Clears storage 
    '''
    requests.delete(url + "clear/v1")

@pytest.fixture
def first_register():
    '''
    Generates the first user
    '''
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
    
    return {'token': token, 'channel_id': channel_id}

@pytest.fixture 
def register_user():
    '''
    Creates a user using the given details and returns the channel_id
    '''
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

@pytest.fixture
def register_channel():
    '''
    Creates a channel using the given details and returns the channel_id
    '''
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


def test_channel_list_valid(clear, first_register, register_channel):
    '''
    Standard test for a valid input/output.

    Expects: 
        Correct output from channel/List
    '''
    token = first_register.get('token')
    channel_id1 = first_register.get('channel_id')

    channel_list = requests.get(url + 'channels/list/v2', params = {'token': token}).json()

    assert channel_list == { 
        'channels': [
            {
                'channel_id': channel_id1, 
                'name': 'channel'
            }
        ]
    }

    channel_id2 = register_channel(token, 'channel2', True)
    channel_list = requests.get(url + 'channels/list/v2', params = {'token': token}).json()

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

def test_channel_list_nochannels(clear, register_user):
    '''
    Testing for an empty list of channels.

    Expects: 
        Correct output from channel/list.
    '''

    no_server_token = register_user('noserver@test.com')
    channel_list = requests.get(url + 'channels/list/v2', params = {'token': no_server_token}).json()

    assert channel_list == { 
        'channels': [

        ]
    }

def test_channel_list_other_owners_test(clear, first_register, register_user, register_channel):
    '''
    Testing if the function returns any channels the user is not part of.

    Expects: 
        Correct output from channel/list
    '''

    token1 = first_register.get('token')
    channel_id1 = first_register.get('channel_id')

    token2 = register_user('owner2@test.com')
    channel_id2 = register_channel(token2, 'channel2', True)

    channel_list1 = requests.get(url + 'channels/list/v2', params = {'token': token1}).json()
    channel_list2 = requests.get(url + 'channels/list/v2', params = {'token': token2}).json()

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

def test_channel_list_after_newjoin_test(clear, first_register, register_user):
    '''
    Tests the case that a user joins a new channel, and looking for an update the the list.

    Expects: 
        Correct output from channel/list
    '''

    channel_id = first_register.get('channel_id')
    token2 = register_user('user2@test.com')

    requests.post(url + 'channel/join/v2', json = {'token': token2, 'channel_id': channel_id})

    channel_list = requests.get(url + 'channels/list/v2', params = {'token': token2}).json()
    assert channel_list == { 
        'channels': [
            {
                'channel_id': channel_id, 
                'name': 'channel'
            }
        ]
    }

def test_invalid_auth_id(clear):
    '''
    Tests whether the auth id is invalid.

    Expects: 
        AccessError (403 error)
    '''

    invalid_token = 1000
    
    invalid_request = requests.get(url + 'channels/list/v2', params = {'token': invalid_token})
    assert (invalid_request.status_code) == 403
