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

def test_leave_member(clear, first_register, register_user):
    '''
    Test standard case

    Expects: 
        Correct output from channel/details.
    '''
    channel_id = first_register.get('channel_id')

    member_token = register_user('member@member.com')

    requests.post(url + 'channel/join/v2', json = {
        'token': member_token, 
        'channel_id': channel_id}
    )

    channel_details = requests.get(url + 'channel/details/v2', params = {
        'token': member_token, 
        'channel_id': channel_id}
    ).json()

    assert channel_details.get('name') == 'channel'

    requests.post(url + 'channel/leave/v1', json = {
        'token': member_token, 
        'channel_id': channel_id}
    )

    assert requests.get(url + 'channel/details/v2', params = {
        'token': member_token, 
        'channel_id': channel_id}
    ).status_code == 403

def test_multiple_leavers(clear, first_register, register_user):
    '''
    Test multiple leavers

    Expects: 
        Correct output from channel/details.
    '''
    channel_id = first_register.get('channel_id')

    member_token1 = register_user('member@member.com')
    member_token2 = register_user('member2@member.com')

    # Joins channel with member1
    requests.post(url + 'channel/join/v2', json = {
        'token': member_token1, 
        'channel_id': channel_id}
    )

    # Joins channel with member2
    requests.post(url + 'channel/join/v2', json = {
        'token': member_token2, 
        'channel_id': channel_id}
    )

    # Tries to get details with member1 channel
    channel_details = requests.get(url + 'channel/details/v2', params = {
        'token': member_token1, 
        'channel_id': channel_id}
    ).json()

    assert channel_details.get('name') == 'channel'

    # Tries to get details with member2 channel
    channel_details = requests.get(url + 'channel/details/v2', params = {
        'token': member_token2, 
        'channel_id': channel_id}
    ).json()

    assert channel_details.get('name') == 'channel'

    # Try again after leaving
    requests.post(url + 'channel/leave/v1', json = {
        'token': member_token1, 
        'channel_id': channel_id}
    )

    assert requests.get(url + 'channel/details/v2', params = {
        'token': member_token1, 
        'channel_id': channel_id}
    ).status_code == 403

    # Try again after leaving
    requests.post(url + 'channel/leave/v1', json = {
        'token': member_token2, 
        'channel_id': channel_id}
    )

    assert requests.get(url + 'channel/details/v2', params = {
        'token': member_token2, 
        'channel_id': channel_id}
    ).status_code == 403

def test_not_in_channel(clear, first_register, register_user):
    '''
    Test not part of channel

    Expects: 
        AccessError (403 error)
    '''

    channel_id = first_register.get('channel_id')

    member_token = register_user('member@member.com')

    assert requests.post(url + 'channel/leave/v1', json = {
        'token': member_token, 
        'channel_id': channel_id}
    ).status_code == 403

def test_invalid_channel_id(clear, register_user):
    '''
    Test invalid channel_id

    Expects: 
        InputError (400 error)
    '''

    member_token = register_user('member@member.com')

    assert requests.post(url + 'channel/leave/v1', json = {
        'token': member_token,
        'channel_id': 123123}
    ).status_code == 400

def test_invalid_token(clear, first_register, register_user):
    '''
    Test invalid token

    Expects: 
        AccessError (403 error)
    '''
    channel_id = first_register.get('channel_id')

    member_token = '-100000'

    assert requests.post(url + 'channel/leave/v1', json = {
        'token': member_token, 
        'channel_id': channel_id}
    ).status_code == 403

def test_messages_remain(clear, first_register, register_user):
    '''
    Test messages remain

    Expects: 
        Correct Output from channel/messages.
    '''

    owner_token = first_register.get('token')
    channel_id = first_register.get('channel_id')

    member_token = register_user('member@member.com')

    requests.post(url + 'channel/join/v2', json = {
        'token': member_token, 
        'channel_id': channel_id
    })

    requests.post(url + 'message/send/v1', json = {
        'token': member_token,
        'channel_id': channel_id,
        'message': 'i like eating apples'
    })

    requests.post(url + 'channel/leave/v1', json = {
        'token': member_token, 
        'channel_id': channel_id
    })

    messages_list = requests.get(url + 'channel/messages/v2', params = {
        'token': owner_token, 
        'channel_id': channel_id,
        'start': 0
    }).json()

    assert messages_list.get('messages')[0].get('message') == 'i like eating apples'

def test_channel_owner_leaves(clear, first_register):
    '''
    Test only channel owner leaves still remains

    Expects: 
        Correct output from channel/list
    '''

    owner_token = first_register.get('token')
    channel_id = first_register.get('channel_id')

    requests.post(url + 'channel/leave/v1', json = {
        'token': owner_token, 
        'channel_id': channel_id}
    )

    channel_list2 = requests.get(url + 'channels/listall/v2', params = {
        'token': owner_token
    }).json()
    
    assert channel_list2 == { 
        'channels': [
            {
                'channel_id': channel_id, 
                'name': 'channel'
            }
        ]
    }

