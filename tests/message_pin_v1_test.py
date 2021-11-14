import pytest
import requests
from datetime import datetime

from src.config import url

@pytest.fixture
def clear():
    '''
    Clears storage 
    '''
    requests.delete(url + "clear/v1")

@pytest.fixture 
def register_user():
    '''
    Create an owner and some users
    '''
    def register_user_function(email):
        user_details = {
            'email': email,
            'password': 'password', 
            'name_first': 'some',
            'name_last': 'user'
        }
        details_dict = requests.post(url + 'auth/register/v2', json = user_details).json()

        return details_dict
    return register_user_function

@pytest.fixture
def extract_token():
    '''
    Extracts the token from a given dictionary.
    '''
    def extract_token_id_function(auth_user_id_dict):
        return auth_user_id_dict['token']
    return extract_token_id_function

@pytest.fixture
def extract_user():
    '''
    Extracts the auth_user_id from a given dictionary.
    '''
    def extract_auth_user_id_function(auth_user_id_dict):
        return auth_user_id_dict['auth_user_id']
    return extract_auth_user_id_function

@pytest.fixture
def extract_message():
    '''
    Extracts the message from a given dictionary
    '''
    def extract_message_id_function(message_id_dict):
        return message_id_dict['message_id']
    return extract_message_id_function

@pytest.fixture
def register_dm():
    '''
    Fixture that creates dms.
    '''
    def create_dm(owner_token, users):
        dm_id = requests.post(url + 'dm/create/v1', json = {
            'token': owner_token,
            'u_ids': users}).json()
        return dm_id['dm_id']
    return create_dm

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

def test_pin_dm(clear, extract_token, extract_user, extract_message, register_user, register_dm):
    '''
    Tests standard valid case

    Expects:
        Correct output from dm/messages/v1
    '''
    owner_details = register_user('owner@email.com')
    owner_id = extract_user(owner_details)
    owner_token = extract_token(owner_details)

    now = datetime.utcnow().timestamp()

    dm_id = register_dm(owner_token, [])

    message_id = extract_message(requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': 'testmessage' 
    }).json())

    requests.post(url + 'message/pin/v1', json = {
        'token': owner_token,
        'message_id': message_id
    })
    
    messages = requests.get(url + 'dm/messages/v1', params = {
        'token': owner_token,
        'dm_id': dm_id, 
        'start': 0 
    }).json()
    
    assert messages == {
        'messages': [
            {
                'message_id': message_id,
                'u_id': owner_id,
                'message': 'testmessage',
                'time_created': pytest.approx(pytest.approx(now, rel=2)),
                'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
                'is_pinned': True
            }
        ],
        'start': 0,
        'end': -1
    }

def test_pin_channel(clear, extract_token, extract_user, extract_message, register_user, register_channel):
    '''
    Tests standard valid case for channels

    Expects:
        Correct output from channel/messages/v2
    '''
    owner_details = register_user('owner@email.com')
    owner_id = extract_user(owner_details)
    owner_token = extract_token(owner_details)

    now = datetime.utcnow().timestamp()

    channel_id = register_channel(owner_token, 'original_channel', True)

    message_id = extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' 
    }).json())

    requests.post(url + 'message/pin/v1', json = {
        'token': owner_token,
        'message_id': message_id
    })

    messages = requests.get(url + 'channel/messages/v2', params = {
        'token': owner_token,
        'channel_id': channel_id, 
        'start': 0 
    }).json()

    assert messages == {
        'messages': [
            {
                'message_id': message_id,
                'u_id': owner_id,
                'message': 'testmessage',
                'time_created': pytest.approx(pytest.approx(now, rel=2)),
                'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
                'is_pinned': True
            }
        ],
        'start': 0,
        'end': -1
    }

def test_invalid_message_id(clear, extract_token, extract_message, register_user, register_channel):
    '''
    Case where message id is not valid.

    Expects:
        InputError(400)
    '''
    owner_details = register_user('owner@email.com')
    owner_token = extract_token(owner_details)

    channel_id = register_channel(owner_token, 'original_channel', True)

    extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' 
    }).json())

    invalid_message_id = -1000

    assert requests.post(url + 'message/pin/v1', json = {
        'token': owner_token,
        'message_id': invalid_message_id
    }).status_code == 400

def test_already_pinned(clear, extract_token, extract_message, register_user, register_channel):
    '''
    Case where message is already pinned.

    Expects:
        InputError(400)
    '''
    owner_details = register_user('owner@email.com')
    owner_token = extract_token(owner_details)

    channel_id = register_channel(owner_token, 'original_channel', True)

    message_id = extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' 
    }).json())

    requests.post(url + 'message/pin/v1', json = {
        'token': owner_token,
        'message_id': message_id
    })

    assert requests.post(url + 'message/pin/v1', json = {
        'token': owner_token,
        'message_id': message_id
    }).status_code == 400

def test_no_owner_perms(clear, extract_token, extract_message, register_user, register_channel):
    '''
    Case where the requestee does not have the correct perms.

    Expects:
        AccessError(403)
    '''
    owner_details = register_user('owner@email.com')
    owner_token = extract_token(owner_details)

    channel_id = register_channel(owner_token, 'original_channel', True)
    message_id = extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' 
    }).json())

    user_info = register_user('randomuser@email.com')
    random_token = extract_token(user_info)

    requests.post(url + 'channel/invite/v2', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'u_id': user_info['auth_user_id']
    })

    assert requests.post(url + 'message/pin/v1', json = {
        'token': random_token,
        'message_id': message_id
    }).status_code == 403

def test_not_member(clear, extract_token, extract_message, register_user, register_channel):
    '''
    Case where requestee is not a member.

    Expects:
        InputError(400)
    '''
    owner_details = register_user('owner@email.com')
    owner_token = extract_token(owner_details)

    channel_id = register_channel(owner_token, 'original_channel', True)
    message_id = extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' 
    }).json())

    user_info = register_user('randomuser@email.com')
    random_token = extract_token(user_info)

    assert requests.post(url + 'message/pin/v1', json = {
        'token': random_token,
        'message_id': message_id
    }).status_code == 400
