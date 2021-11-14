import pytest
import requests
from src.config import url
from time import sleep
from datetime import datetime, timezone

@pytest.fixture
def clear():
    '''
    Clears the datastore.
    '''
    requests.delete(url + 'clear/v1')

@pytest.fixture
def register_users(clear):
    '''
    Registers a user.
    '''
    owner_id = requests.post(url + 'auth/register/v2', json = {
        'email': 'owner@test.com', 
        'password': 'password', 
        'name_first': 'owner',
        'name_last': 'one' }
        ).json()

    user1_id = requests.post(url + 'auth/register/v2', json = {
        'email': 'user@test.com', 
        'password': 'password', 
        'name_first': 'user',
        'name_last': 'one' }
    ).json()
    return [owner_id, user1_id]

@pytest.fixture
def dm_factory():
    '''
    Fixture that creates dms.
    '''
    def create_dm(owner_token, users):
        dm_id = requests.post(url + 'dm/create/v1', json = {
            'token': owner_token,
            'u_ids': users}).json()
        return dm_id['dm_id']
    return create_dm

def test_standard(register_users, dm_factory):
    '''
    Standard valid test case.

    Expects:
        Correct output from dm/messages/v1
    '''
    dm_id = dm_factory(register_users[0]['token'], [])

    now = int(datetime.now(timezone.utc).timestamp())
    message_id = requests.post(url + 'message/sendlaterdm/v1', json={
        'token': register_users[0]['token'],
        'dm_id': dm_id,
        'message': 'hi there',
        'time_sent': now + 1
    }).json().get('message_id')

    messages_dict = requests.get(url + 'dm/messages/v1', params = {
        'token': register_users[0]['token'],
        'dm_id': dm_id,
        'start': 0
    }).json()

    assert messages_dict == {
        'messages': [],
        'start': 0,
        'end': -1
    }

    sleep(2)

    messages_dict = requests.get(url + 'dm/messages/v1', params = {
        'token': register_users[0]['token'],
        'dm_id': dm_id,
        'start': 0
    }).json()
    assert messages_dict == {
        'messages': [
            {
                'message_id': message_id,
                'u_id': register_users[0]['auth_user_id'],
                'message': 'hi there',
                'time_created': pytest.approx(now + 2, rel=1),
                'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1
    }

def test_multiple(register_users, dm_factory):
    '''
    Standard valid test case with multiple messages.

    Expects:
        Correct output from dm/messages/v1
    '''
    dm_id = dm_factory(register_users[0]['token'], [])

    now = int(datetime.now(timezone.utc).timestamp())
    message_id_1 = requests.post(url + 'message/sendlaterdm/v1', json={
        'token': register_users[0]['token'],
        'dm_id': dm_id,
        'message': 'hi there',
        'time_sent': now + 2
    }).json().get('message_id')

    message_id_2 = requests.post(url + 'message/sendlaterdm/v1', json={
        'token': register_users[0]['token'],
        'dm_id': dm_id,
        'message': 'hi there',
        'time_sent': now + 1
    }).json().get('message_id')

    message_id_3 = requests.post(url + 'message/sendlaterdm/v1', json={
        'token': register_users[0]['token'],
        'dm_id': dm_id,
        'message': 'hi there',
        'time_sent': now + 3
    }).json().get('message_id')

    messages_dict = requests.get(url + 'dm/messages/v1', params = {
        'token': register_users[0]['token'],
        'dm_id': dm_id,
        'start': 0
    }).json()

    assert messages_dict == {
        'messages': [],
        'start': 0,
        'end': -1
    }

    sleep(4)

    messages_dict = requests.get(url + 'dm/messages/v1', params = {
        'token': register_users[0]['token'],
        'dm_id': dm_id,
        'start': 0
    }).json()

    assert messages_dict == {
        'messages': [
            {
                'message_id': message_id_3,
                'u_id': register_users[0]['auth_user_id'],
                'message': 'hi there',
                'time_created': pytest.approx(now + 3, rel=1),
                'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
                'is_pinned': False
            },
            {
                'message_id': message_id_1,
                'u_id': register_users[0]['auth_user_id'],
                'message': 'hi there',
                'time_created': pytest.approx(now + 2, rel=1),
                'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
                'is_pinned': False
            },
            {
                'message_id': message_id_2,
                'u_id': register_users[0]['auth_user_id'],
                'message': 'hi there',
                'time_created': pytest.approx(now + 1, rel=1),
                'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1
    }

def test_invalid_dm(register_users):
    '''
    Test case where dm_id is invalid.

    Expects:
        InputError(400)
    '''
    
    assert requests.post(url + 'message/sendlaterdm/v1', json={
        'token': register_users[0]['token'],
        'dm_id': 123123,
        'message': 'hi there',
        'time_sent': int(datetime.now(timezone.utc).timestamp()) + 2
    }).status_code == 400

def test_msg_length(register_users, dm_factory):
    '''
    Test case where message is too long.

    Expects:
        InputError(400)
    '''
    dm_id = dm_factory(register_users[0]['token'], [])

    assert requests.post(url + 'message/sendlaterdm/v1', json={
        'token': register_users[0]['token'],
        'dm_id': dm_id,
        'message': 'hi there' * 1000,
        'time_sent': int(datetime.now(timezone.utc).timestamp()) + 2
    }).status_code == 400

def test_time_in_past(register_users, dm_factory):
    '''
    Test case where the progrma attempts to trvel back in  time.

    Expects:
        InputError(400)
    '''
    dm_id = dm_factory(register_users[0]['token'], [])
    
    assert requests.post(url + 'message/sendlaterdm/v1', json={
        'token': register_users[0]['token'],
        'dm_id': dm_id,
        'message': 'hi there',
        'time_sent': int(datetime.now(timezone.utc).timestamp()) - 2
    }).status_code == 400

def test_dm_valid_user_not_in_channel(register_users, dm_factory):
    '''
    Test case where user is not a part of the dm.

    Expects:
        AccessError(403)
    '''

    dm_id = dm_factory(register_users[0]['token'], [])
    
    assert requests.post(url + 'message/sendlaterdm/v1', json={
        'token': register_users[1]['token'],
        'dm_id': dm_id,
        'message': 'hi there',
        'time_sent': int(datetime.now(timezone.utc).timestamp()) + 2
    }).status_code == 403

def test_token_invalid(register_users, dm_factory):
    '''
    Test case where the token is invalid.

    Expects:
        AccessError(403)
    '''
    dm_id = dm_factory(register_users[0]['token'], [])

    assert requests.post(url + 'message/sendlaterdm/v1', json={
        'token': '123123',
        'dm_id': dm_id,
        'message': 'hi there',
        'time_sent': int(datetime.now(timezone.utc).timestamp()) + 2
    }).status_code == 403

