from _pytest.python_api import approx
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

# Extracts the dm from a given dictionary.
@pytest.fixture
def extract_dm():
    def extract_dm_id_function(dm_id_dict):
        return dm_id_dict['dm_id']
    return extract_dm_id_function

# Extracts the message from a given dictionary
@pytest.fixture
def extract_message():
    def extract_message_id_function(message_id_dict):
        return message_id_dict['message_id']
    return extract_message_id_function

# Creates the details required for sending message
def create_message_details():
    def create_message_details_function(owner_token, dm_id, textmessage):
        return {
            'token': owner_token,
            'dm_id': dm_id, 
            'start': 0 
        }
    return create_message_details_function

@pytest.fixture
def clear():
    requests.delete(url + 'clear/v1')

# Automatically create owner user id and dm id. Both are 1 by default.
@pytest.fixture
def register():
    owner_id_dict = requests.post(url + 'auth/register/v2', json = {
        'email': 'owner@test.com', 
        'password': 'password', 
        'name_first': 'owner',
        'name_last': 'one' }
        ).json()
    owner_user_token = owner_id_dict['token']
    user_id_dict = requests.post(url + 'auth/register/v2', json = {
        'email': 'user@test.com', 
        'password': 'password', 
        'name_first': 'user',
        'name_last': 'one' }
        ).json() 
    
    dm_id_dict = requests.post(url + 'dm/create/v1', json = {
        'token': owner_user_token,
        'u_ids': [user_id_dict['auth_user_id']]}
        ).json()

    return {**owner_id_dict, **dm_id_dict}

def test_senddm_one_valid_message(clear, register, extract_token, extract_user, extract_dm, extract_message):
    dm_id = extract_dm(register)
    owner_token = extract_token(register)
    now = datetime.utcnow().timestamp()
    message_id = extract_message(requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': 'testmessage' }).json())
    messages = requests.get(url + 'dm/messages/v1', params = {
        'token': owner_token,
        'dm_id': dm_id, 
        'start': 0 }).json()
    
    assert messages == {
        'messages': [
            {
                'message_id': message_id,
                'u_id': extract_user(register),
                'message': 'testmessage',
                'time_created': pytest.approx(pytest.approx(now, rel=2))
            }
        ],
        'start': 0,
        'end': -1
    }

def test_senddm_multiple_valid_messages(clear, register, extract_token, extract_user, extract_dm, extract_message):
    '''
    Standard test with one message.

    Expects: 
        Correct output from channel/messages.
    '''

    dm_id = extract_dm(register)
    owner_token = extract_token(register)
    owner_id = extract_user(register)
    now1 = datetime.utcnow().timestamp()
    message_id0 = extract_message(requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': 'testmessage0' }).json())
    now2 = datetime.utcnow().timestamp()
    message_id1 = extract_message(requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': 'testmessage1' }).json())
    now3 = datetime.utcnow().timestamp()
    message_id2 = extract_message(requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': 'testmessage2' }).json())

    messages = requests.get(url + 'dm/messages/v1', params = {
        'token': owner_token,
        'dm_id': dm_id, 
        'start': 0 }).json()

    assert messages == {
        'messages': [
            {
                'message_id': message_id2,
                'u_id': owner_id,
                'message': 'testmessage2',
                'time_created': pytest.approx(now1, rel=2)
            },
            {
                'message_id': message_id1,
                'u_id': owner_id,
                'message': 'testmessage1',
                'time_created': pytest.approx(now2, rel=2)
            },
            {
                'message_id': message_id0,
                'u_id': owner_id,
                'message': 'testmessage0',
                'time_created':  pytest.approx(now3, rel=2)
            }
            ],
        'start': 0,
        'end': -1
    }

    assert extract_message(messages['messages'][0]) != extract_message(messages['messages'][1]) != extract_message(messages['messages'][2])

def test_senddm_51_valid_messages(clear, register, extract_token, extract_user, extract_dm, extract_message):
    '''
    Standard test with multiple messages.

    Expects: 
        Correct output from channel/messages.
    '''

    dm_id = extract_dm(register)
    owner_token = extract_token(register)

    for _ in range(51):
        requests.post(url + 'message/senddm/v1', json = {
            'token': owner_token,
            'dm_id': dm_id,
            'message': 'testmessage' }).json()

    messages = requests.get(url + 'dm/messages/v1', params = {
        'token': owner_token,
        'dm_id': dm_id, 
        'start': 0 }).json()

    for specific_message_info in messages['messages']:
        assert specific_message_info['message'] == "testmessage"

    assert messages['start'] == 0
    assert messages['end'] == 50

    assert extract_message(messages['messages'][0]) != extract_message(messages['messages'][1]) != extract_message(messages['messages'][2])


def test_senddm_invalid_message_to_short(clear, register, extract_token, extract_dm):
    '''
    Test case where message sent is too short.

    Expects: 
        InputError (400 error)
    '''

    dm_id = extract_dm(register)
    owner_token = extract_token(register)

    assert requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': ''
    }).status_code == 400

def test_senddm_invalid_message_to_long(clear, register, extract_token, extract_dm):
    '''
    Test case where message sent is too long.

    Expects: 
        InputError (400 error)
    '''

    dm_id = extract_dm(register)
    owner_token = extract_token(register)
    
    assert requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': 'a' * 1001
    }).status_code == 400

def test_senddm_valid_message_unauthorized_user(clear, register, extract_token, extract_dm):
    '''
    Test case where user is not authorized to send a message.

    Expects: 
        AccessError (403 error)
    '''

    dm_id = extract_dm(register)
    user_token = extract_token(requests.post(url + 'auth/register/v2', json = {
    'email': 'user1@test.com', 
    'password': 'password', 
    'name_first': 'user',
    'name_last': 'one' }
    ).json())
    assert requests.post(url + 'message/senddm/v1', json = {
        'token': user_token,
        'dm_id': dm_id,
        'message': '123456'
    }).status_code == 403

def test_senddm_message_invalid_dm_id(clear, register, extract_token, extract_user, extract_message):
    '''
    Test case where dm_id is invalid.

    Expects: 
        InputError (400 error)
    '''

    owner_token = extract_token(register)
    assert requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': 123123,
        'message': '123123'
    }).status_code == 400

def test_senddm_valid_message_invalid_token(clear, register, extract_token):
    '''
    Test case where token is not valid.

    Expects: 
        AccessError (403 error)
    '''

    dm_id = extract_token(register)
    assert requests.post(url + 'message/senddm/v1', json = {
        'token': '123123414',
        'dm_id': dm_id,
        'message': 'asds'
    }).status_code == 403

def test_senddm_invalid__invalid_token(clear, register):
    '''
    Test case where access error is expected to take precedence.

    Expects: 
        AccessError (403 error)
    '''

    assert requests.post(url + 'message/senddm/v1', json = {
        'token': '123123414',
        'dm_id': 23423,
        'message': ''
    }).status_code == 403
