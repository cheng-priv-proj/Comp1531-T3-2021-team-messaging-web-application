import pytest
import requests
from datetime import datetime

from src.config import url

# Clears storage 
@pytest.fixture
def clear():
    requests.delete(url + "clear/v1")

# Create an owner and some users
@pytest.fixture 
def register_user():
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

# Extracts the token from a given dictionary.
@pytest.fixture
def extract_token():
    def extract_token_id_function(auth_user_id_dict):
        return auth_user_id_dict['token']
    return extract_token_id_function

# Extracts the auth_user_id from a given dictionary.
@pytest.fixture
def extract_user():
    def extract_auth_user_id_function(auth_user_id_dict):
        return auth_user_id_dict['auth_user_id']
    return extract_auth_user_id_function

# Extracts the message from a given dictionary
@pytest.fixture
def extract_message():
    def extract_message_id_function(message_id_dict):
        return message_id_dict['message_id']
    return extract_message_id_function

@pytest.fixture
def register_dm():
    def create_dm(owner_token, users):
        dm_id = requests.post(url + 'dm/create/v1', json = {
            'token': owner_token,
            'u_ids': users}).json()
        return dm_id['dm_id']
    return create_dm

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

def test_dm_share(clear, extract_token, extract_user, extract_message, register_user, register_dm):
    owner_details = register_user('owner@email.com')
    owner_id = extract_user(owner_details)
    owner_token = extract_token(owner_details)

    now = datetime.utcnow().timestamp()

    dm_id = register_dm(owner_token, [])
    dm_id_sent_to = register_dm(owner_token, [])

    message_id = extract_message(requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': 'testmessage' 
    }).json())
    
    shared_message_id_dict = requests.post(url + 'message/share/v1', json = { 
        'token': owner_token, 
        'og_message_id': message_id, 
        'message': '', 
        'channel_id': -1, 
        'dm_id': dm_id_sent_to 
    }).json()
    shared_message_id = shared_message_id_dict.get('shared_message_id')
    print(owner_token)
    messages = requests.get(url + 'dm/messages/v1', params= {
        'token': owner_token,
        'dm_id': dm_id_sent_to, 
        'start': 0 
    }).json()
    
    assert messages == {
        'messages': [
            {
                'message_id': shared_message_id,
                'u_id': owner_id,
                'message': 'testmessage',
                'time_created': pytest.approx(pytest.approx(now, rel=2)),
                'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1
    }

def test_channel_share(clear, extract_token, extract_user, extract_message, register_user, register_channel):
    owner_details = register_user('owner@email.com')
    owner_id = extract_user(owner_details)
    owner_token = extract_token(owner_details)

    now = datetime.utcnow().timestamp()

    channel_id = register_channel(owner_token, 'original_channel', True)
    channel_id_sent_to = register_channel(owner_token, 'sent_to_channel', True)

    message_id = extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' 
    }).json())

    shared_message_id_dict = requests.post(url + 'message/share/v1', json = { 
        'token': owner_token, 
        'og_message_id': message_id, 
        'message': '', 
        'channel_id': channel_id_sent_to, 
        'dm_id': -1
    }).json()
    shared_message_id = shared_message_id_dict.get('shared_message_id')

    messages = requests.get(url + 'channel/messages/v2', params= {
        'token': owner_token,
        'channel_id': channel_id_sent_to, 
        'start': 0 
    }).json()

    assert messages == {
        'messages': [
            {
                'message_id': shared_message_id,
                'u_id': owner_id,
                'message': 'testmessage',
                'time_created': pytest.approx(pytest.approx(now, rel=2)),
                'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1
    }

def test_extra_message(clear, extract_token, extract_user, extract_message, register_user, register_channel):
    owner_details = register_user('owner@email.com')
    owner_id = extract_user(owner_details)
    owner_token = extract_token(owner_details)

    now = datetime.utcnow().timestamp()

    channel_id = register_channel(owner_token, 'original_channel', True)
    channel_id_sent_to = register_channel(owner_token, 'sent_to_channel', True)

    message_id = extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' 
    }).json())

    shared_message_id_dict = requests.post(url + 'message/share/v1', json = { 
        'token': owner_token, 
        'og_message_id': message_id, 
        'message': 'extramessage', 
        'channel_id': channel_id_sent_to, 
        'dm_id': -1
    }).json()
    shared_message_id = shared_message_id_dict.get('shared_message_id')

    messages = requests.get(url + 'channel/messages/v2', params= {
        'token': owner_token,
        'channel_id': channel_id_sent_to, 
        'start': 0 
    }).json()

    assert messages == {
        'messages': [
            {
                'message_id': shared_message_id,
                'u_id': owner_id,
                'message': 'testmessageextramessage',
                'time_created': pytest.approx(pytest.approx(now, rel=2)),
                'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1
    }

def test_both_channel_id_and_dm_id_invalid(clear, extract_token, extract_message, register_user, register_channel):
    owner_details = register_user('owner@email.com')
    owner_token = extract_token(owner_details)

    channel_id = register_channel(owner_token, 'original_channel', True)

    message_id = extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' 
    }).json())

    invalid_channel_id = -1000

    assert requests.post(url + 'message/share/v1', json = { 
        'token': owner_token, 
        'og_message_id': message_id, 
        'message': '', 
        'channel_id': invalid_channel_id, 
        'dm_id': -1
    }).status_code == 400

def test_neither_negative_one(clear, extract_token, extract_user, extract_message, register_user, register_channel, register_dm):
    owner_details = register_user('owner@email.com')
    owner_token = extract_token(owner_details)

    channel_id = register_channel(owner_token, 'original_channel', True)
    dm_id = register_dm(owner_token, [])

    message_id = extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' 
    }).json())

    assert requests.post(url + 'message/share/v1', json = { 
        'token': owner_token, 
        'og_message_id': message_id, 
        'message': '', 
        'channel_id': channel_id, 
        'dm_id': dm_id
    }).status_code == 400

def test_invalid_og_message_id(clear, extract_token, extract_message, register_user, register_channel):
    owner_details = register_user('owner@email.com')
    owner_token = extract_token(owner_details)

    channel_id = register_channel(owner_token, 'original_channel', True)

    extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' 
    }).json())

    invalid_message_id = -1000

    assert requests.post(url + 'message/share/v1', json = { 
        'token': owner_token, 
        'og_message_id': invalid_message_id, 
        'message': '', 
        'channel_id': channel_id, 
        'dm_id': -1
    }).status_code == 400

def test_length_of_messages_less_than_thousand(clear, extract_token, extract_message, register_user, register_channel):
    owner_details = register_user('owner@email.com')
    owner_token = extract_token(owner_details)

    channel_id = register_channel(owner_token, 'original_channel', True)
    channel_id_sent_to = register_channel(owner_token, 'sent_to_channel', True)

    message_id = extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' 
    }).json())

    assert requests.post(url + 'message/share/v1', json = { 
        'token': owner_token, 
        'og_message_id': message_id, 
        'message': 'extramessage' * 1000, 
        'channel_id': channel_id_sent_to, 
        'dm_id': -1
    }).status_code == 400
    

def test_valid_id_but_not_in_channel(clear, extract_token, extract_message, register_user, register_channel):
    owner_details = register_user('owner@email.com')
    owner_token = extract_token(owner_details)

    channel_id = register_channel(owner_token, 'original_channel', True)

    message_id = extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' 
    }).json())

    random_token = extract_token(register_user('randomuser@email.com'))

    assert requests.post(url + 'message/share/v1', json = { 
        'token': random_token, 
        'og_message_id': message_id, 
        'message': '', 
        'channel_id': channel_id, 
        'dm_id': -1
    }).status_code == 403

