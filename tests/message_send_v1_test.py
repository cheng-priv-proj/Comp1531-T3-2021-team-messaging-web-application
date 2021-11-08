import pytest
import requests
from datetime import datetime

from src.config import url

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

# Extracts the channel from a given dictionary.
@pytest.fixture
def extract_channel():
    def extract_channel_id_function(channel_id_dict):
        return channel_id_dict['channel_id']
    return extract_channel_id_function

# Extracts the message from a given dictionary
@pytest.fixture
def extract_message():
    def extract_message_id_function(message_id_dict):
        return message_id_dict['message_id']
    return extract_message_id_function

@pytest.fixture
def clear():
    requests.delete(url + 'clear/v1')

# Automatically create owner user id and channel id. Both are 1 by default.
@pytest.fixture
def register():
    owner_id_dict = requests.post(url + 'auth/register/v2', json = {
        'email': 'owner@test.com', 
        'password': 'password', 
        'name_first': 'owner',
        'name_last': 'one' }
        ).json()
    owner_user_token = owner_id_dict['token']
    channel_id_dict = requests.post(url + 'channels/create/v2', json = {
        'token': owner_user_token,
        'name': 'channel_name', 
        'is_public': True }).json()

    return {**owner_id_dict, **channel_id_dict}

def test_send_one_valid_message(clear, register, extract_token, extract_user, extract_channel, extract_message):
    '''
    Standard test with one message.

    Expects: 
        Correct output from channel/messages.
    '''

    channel_id = extract_channel(register)
    owner_token = extract_token(register)
    now = datetime.utcnow().timestamp()

    message_id = requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' }).json()
    messages = requests.get(url + 'channel/messages/v2', params = {
        'token': owner_token,
        'channel_id': channel_id, 
        'start': 0 }).json()
    print(messages)
    assert messages == {
        'messages': [
            {
                'message_id': message_id.get('message_id'),
                'u_id': extract_user(register),
                'message': 'testmessage',
                'time_created':  pytest.approx(now, rel=2),
<<<<<<< HEAD
                'reacts': [
                    {  
                    'react_id' : 1,
                    'u_ids' : [],
                    'is_this_user_reacted' : False
                    }
                ],
=======
                'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
>>>>>>> b3ccab81e3179ca57ca8c7e541d016eaf26e37c0
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1
    }

def test_send_multiple_valid_messages(clear, register, extract_token, extract_user, extract_channel, extract_message):
    '''
    Standard test with multiple messages.

    Expects: 
        Correct output from channel/messages.
    '''

    channel_id = extract_channel(register)
    owner_token = extract_token(register)
    owner_id = extract_user(register)
    now = datetime.utcnow().timestamp()
    message_id0 = extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage0' }).json())
    message_id1 = extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage1' }).json())
    message_id2 = extract_message(requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage2' }).json())
    messages = requests.get(url + 'channel/messages/v2', params = {
        'token': owner_token,
        'channel_id': channel_id, 
        'start': 0 }).json()
    print(messages)
    assert messages == {
        'messages': [
            {
                'message_id': message_id2,
                'u_id': owner_id,
                'message': 'testmessage2',
                'time_created': pytest.approx(now, rel=2),
<<<<<<< HEAD
                'reacts': [
                    {  
                    'react_id' : 1,
                    'u_ids' : [],
                    'is_this_user_reacted' : False
                    }
                ],
=======
                'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
>>>>>>> b3ccab81e3179ca57ca8c7e541d016eaf26e37c0
                'is_pinned': False
            },
            {
                'message_id': message_id1,
                'u_id': owner_id,
                'message': 'testmessage1',
                'time_created': pytest.approx(now, rel=2),
<<<<<<< HEAD
                'reacts': [
                    {  
                    'react_id' : 1,
                    'u_ids' : [],
                    'is_this_user_reacted' : False
                    }
                ],
=======
                'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
>>>>>>> b3ccab81e3179ca57ca8c7e541d016eaf26e37c0
                'is_pinned': False
            },
            {
                'message_id': message_id0,
                'u_id': owner_id,
                'message': 'testmessage0',
                'time_created':  pytest.approx(now, rel=2),
<<<<<<< HEAD
                'reacts': [
                    {  
                    'react_id' : 1,
                    'u_ids' : [],
                    'is_this_user_reacted' : False
                    }
                ],
=======
                'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
>>>>>>> b3ccab81e3179ca57ca8c7e541d016eaf26e37c0
                'is_pinned': False
            }
            ],
        'start': 0,
        'end': -1
    }

    assert extract_message(messages['messages'][0]) != extract_message(messages['messages'][1]) != extract_message(messages['messages'][2])

def test_send_invalid_message_to_short(clear, register, extract_token, extract_channel):
    '''
    Test case where message sent is too short.

    Expects: 
        InputError (400 error)
    '''

    channel_id = extract_channel(register)
    owner_token = extract_token(register)

    assert requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': '',
        'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}]
    }).status_code == 400

def test_send_invalid_message_to_long(clear, register, extract_token, extract_channel):
    '''
    Test case where message sent is too long.

    Expects: 
        InputError (400 error)
    '''

    channel_id = extract_channel(register)
    owner_token = extract_token(register)
    
    assert requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'a' * 1001,
        'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}]
    }).status_code == 400

def test_send_valid_message_unauthorized_user(clear, register, extract_token, extract_channel):
    '''
    Test case where user is not authorized to send a message.

    Expects: 
        AccessError (403 error)
    '''

    channel_id = extract_channel(register)
    user_token = extract_token(requests.post(url + 'auth/register/v2', json = {
    'email': 'user@test.com', 
    'password': 'password', 
    'name_first': 'user',
    'name_last': 'one' }
    ).json())
    assert requests.post(url + 'message/send/v1', json = {
        'token': user_token,
        'channel_id': channel_id,
        'message': '123456'
    }).status_code == 403

def test_send_message_invalid_channel_id(clear, register, extract_token, extract_user, extract_message):
    '''
    Test case where channel_id is invalid.

    Expects: 
        InputError (400 error)
    '''

    owner_token = extract_token(register)
    assert requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': 123123,
        'message': '123123'
    }).status_code == 400

def test_send_valid_message_invalid_token(clear, register, extract_token):
    '''
    Test case where token is not valid.

    Expects: 
        AccessError (403 error)
    '''

    channel_id = extract_token(register)
    assert requests.post(url + 'message/send/v1', json = {
        'token': '123123414',
        'channel_id': channel_id,
        'message': 'asds'
    }).status_code == 403

def test_send_invalid_message_invalid_token(clear, register):
    '''
    Test case where access error is expected to take precedence.

    Expects: 
        AccessError (403 error)
    '''

    assert requests.post(url + 'message/send/v1', json = {
        'token': '123123414',
        'channel_id': 23423,
        'message': ''
    }).status_code == 403


