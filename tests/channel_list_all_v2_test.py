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
    
    return {'token': token, 'channel_id': int(channel_id)}

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

def test_channel_list_all_valid(clear, first_register, register_channel):
    '''
    Testing the standard valid case.

    Expects: 
        Correct output from channel/listall.
    '''
    token = first_register.get('token')
    channel_id1 = first_register.get('channel_id')
    
    channel_list = requests.get(url + 'channels/listall/v2', params = {'token': token}).json()

    assert channel_list == { 
        'channels': [
            {
                'channel_id': channel_id1, 
                'name': 'channel'
            }
        ]
    }

    channel_id2 = register_channel(token, 'channel2', True)
    channel_list2 = requests.get(url + 'channels/listall/v2', params = {'token': token}).json()
    
    assert channel_list2 == { 
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

def test_channel_list_all_nochannels(clear, register_user):
    '''
    Testing the case where there are no channels.

    Expects: 
        Correct output from channel/listall.
    '''

    token = register_user('noserver@test.com')
    channel_list = requests.get(url + 'channels/listall/v2', params = {'token': token}).json()

    assert channel_list == { 
        'channels': [

        ]
    }

def test_channel_list_all_other_owners(clear, first_register, register_user, register_channel):
    '''
    Testing that the function returns all channels regardless whether or not the auth id is part of them

    Expects: 
        Correct Output from channel/listall
    '''

    token1 = first_register.get('token')
    channel_id1 = first_register.get('channel_id')

    token2 = register_user('owner2@test.com')
    channel_id2 = register_channel(token2, 'channel2', True)

    channel_list = requests.get(url + 'channels/listall/v2', params = {'token': token1}).json()
    channel_list2 = requests.get(url + 'channels/listall/v2', params = {'token': token2}).json()

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

    assert channel_list2 == { 
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

def test_channel_list_all_public_private(clear, first_register, register_user, register_channel):
    '''
    Testing that whether a channel is public or private has no effect on the returning list.

    Expects: 
        Correct Output from channel/listall
    '''

    token1 = first_register.get('token')
    channel_id1 = first_register.get('channel_id')

    token2 = register_user('owner2@test.com')
    channel_id2 = register_channel(token2, 'channel2', True)

    token3 = register_user('owner3@test.com')
    channel_id3 = register_channel(token3, 'channel3', True)

    channel_list = requests.get(url + 'channels/listall/v2', params = {'token': token1}).json()
    channel_list2 = requests.get(url + 'channels/listall/v2', params = {'token': token2}).json()
    channel_list3 = requests.get(url + 'channels/listall/v2', params = {'token': token3}).json()

    assert channel_list == { 
        'channels': [
            {
                'channel_id': channel_id1, 
                'name': 'channel'
            }, 
            {
                'channel_id': channel_id2, 
                'name': 'channel2'
            },
            {
                'channel_id': channel_id3, 
                'name': 'channel3'
            }
        ]
    }
    assert channel_list2 == { 
        'channels': [
            {
                'channel_id': channel_id1, 
                'name': 'channel'
            }, 
            {
                'channel_id': channel_id2, 
                'name': 'channel2'
            },
            {
                'channel_id': channel_id3, 
                'name': 'channel3'
            }
        ]
    }
    assert channel_list3 == { 
        'channels': [
            {
                'channel_id': channel_id1, 
                'name': 'channel'
            }, 
            {
                'channel_id': channel_id2, 
                'name': 'channel2'
            },
            {
                'channel_id': channel_id3, 
                'name': 'channel3'
            }
        ]
    }

def test_invalid_auth_id(clear):
    '''
    Tests whether the auth id is invalid.

    Expects: 
        AccessError (403 error)
    '''

    invalid_token = '1000'
    
    invalid_request = requests.get(url + 'channels/listall/v2', params = {'token': invalid_token})
    assert (invalid_request.status_code) == 403
