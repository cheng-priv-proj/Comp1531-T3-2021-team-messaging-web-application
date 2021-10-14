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
@pytest.mark.skip
def test_senddm_one_valid_message(clear, register, extract_token, extract_user, extract_dm, extract_message):
    dm_id = extract_dm(register)
    owner_token = extract_token(register)
    now = datetime.utcnow().timestamp()
    message_id = extract_message(requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': 'testmessage' }).json())
    messages = requests.get(url + 'message/senddm/v1', params = {
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
@pytest.mark.skip
def test_senddm_multiple_valid_messages(clear, register, extract_token, extract_user, extract_dm, extract_message):
    dm_id = extract_dm(register)
    owner_token = extract_token(register)
    owner_id = extract_user(register)
    now = datetime.utcnow().timestamp()
    message_id0 = extract_message(requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': 'testmessage' }).json())
    message_id1 = extract_message(requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': 'testmessage0' }).json())
    message_id2 = extract_message(requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': 'testmessage2' }).json())
    messages = requests.get(url + 'message/senddm/v1', params = {
        'token': owner_token,
        'dm_id': dm_id, 
        'start': 0 }).json()

    assert messages == {
        'messages': [
            {
                'message_id': message_id2,
                'u_id': owner_id,
                'message': 'testmessage1',
                'time_created': pytest.approx(now, rel=2)
            },
            {
                'message_id': message_id1,
                'u_id': owner_id,
                'message': 'testmessage0',
                'time_created': pytest.approx(now, rel=2)
            },
            {
                'message_id': message_id0,
                'u_id': owner_id,
                'message': 'testmessage',
                'time_created':  pytest.approx(now, rel=2)
            }
            ],
        'start': 0,
        'end': -1
    }

    assert extract_message(messages[0]) != extract_message(messages[1]) != extract_message(messages[2])
@pytest.mark.skip
def test_senddm_invalid_message_to_short(clear, register, extract_token, extract_dm):
    dm_id = extract_dm(register)
    owner_token = extract_token(register)

    assert requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': ''
    }).status_code == 400
@pytest.mark.skip
def test_senddm_invalid_message_to_long(clear, register, extract_token, extract_dm):
    dm_id = extract_dm(register)
    owner_token = extract_token(register)
    
    assert requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': dm_id,
        'message': 'a' * 1001
    }).status_code == 400
@pytest.mark.skip
def test_senddm_valid_message_unauthorized_user(clear, register, extract_token, extract_dm):
    dm_id = extract_dm(register)
    user_token = extract_token(requests.post(url + 'auth/register/v2', json = {
    'email': 'user@test.com', 
    'password': 'password', 
    'name_first': 'user',
    'name_last': 'one' }
    ).json())
    assert requests.post(url + 'message/senddm/v1', json = {
        'token': user_token,
        'dm_id': dm_id,
        'message': '123456'
    }).status_code == 403
@pytest.mark.skip
def test_senddm_message_invalid_dm_id(clear, register, extract_token, extract_user, extract_message):
    owner_token = extract_token(register)
    assert requests.post(url + 'message/senddm/v1', json = {
        'token': owner_token,
        'dm_id': 123123,
        'message': '123123'
    })
@pytest.mark.skip
def test_senddm_valid_message_invalid_token(clear, register, extract_token):
    dm_id = extract_token(register)
    assert requests.post(url + 'message/senddm/v1', json = {
        'token': '123123414',
        'dm_id': dm_id,
        'message': 'asds'
    }).status_code == 403
@pytest.mark.skip
def test_senddm_invalid__invalid_token(clear, register):
    assert requests.post(url + 'message/senddm/v1', json = {
        'token': '123123414',
        'dm_id': 23423,
        'message': ''
    }).status_code == 403

# valid dm id
# valid length of message too small and too long
# authorized user 
# unique message id
# correct types