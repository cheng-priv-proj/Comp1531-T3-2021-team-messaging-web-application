import pytest
import requests
from src.config import url
from time import sleep
from datetime import datetime

@pytest.fixture
def clear():
    requests.delete(url + 'clear/v1')

@pytest.fixture
def register_users(clear):
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
def channel_factory():
    def create_channel(owner_token):
        channel_id = requests.post(url + 'channels/create/v2', json = {
            'token': owner_token,
            'name': 'channel',
            'is_public': True
        }).json()
        return channel_id['channel_id']
    return create_channel

def test_standard(register_users, channel_factory):
    channel_id = channel_factory(register_users[0]['token'])

    now = datetime.utcnow().timestamp()
    message_id = requests.post(url + 'message/sendlater/v1', json={
        'token': register_users[0]['token'],
        'channel_id': channel_id,
        'message': 'hi there',
        'time_sent': now + 2
    }).json()
    
    message_id = message_id.get('message_id')

    messages_dict = requests.get(url + 'channel/messages/v2', params = {
        'token': register_users[0]['token'],
        'channel_id': channel_id,
        'start': 0
    }).json()

    assert messages_dict == {
        'messages': [],
        'start': 0,
        'end': -1
    }

    sleep(3)

    messages_dict = requests.get(url + 'channel/messages/v2', params = {
        'token': register_users[0]['token'],
        'channel_id': channel_id,
        'start': 0
    }).json()

    print(messages_dict)

    assert messages_dict == {
        'messages': [
            {
                'message_id': message_id,
                'u_id': register_users[0]['auth_user_id'],
                'message': 'hi there',
                'time_created': pytest.approx(now + 2, rel=1),
                'reacts': [],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1
    }

def test_multiple(register_users, channel_factory):
    channel_id = channel_factory(register_users[0]['token'])

    now = datetime.utcnow().timestamp()
    message_id_1 = requests.post(url + 'message/sendlater/v1', json={
        'token': register_users[0]['token'],
        'channel_id': channel_id,
        'message': 'hi there',
        'time_sent': now + 2
    }).json().get('message_id')

    message_id_2 = requests.post(url + 'message/sendlater/v1', json={
        'token': register_users[0]['token'],
        'channel_id': channel_id,
        'message': 'hi there',
        'time_sent': now + 1
    }).json().get('message_id')

    message_id_3 = requests.post(url + 'message/sendlater/v1', json={
        'token': register_users[0]['token'],
        'channel_id': channel_id,
        'message': 'hi there',
        'time_sent': now + 5
    }).json().get('message_id')

    messages_dict = requests.get(url + 'channel/messages/v2', params = {
        'token': register_users[0]['token'],
        'channel_id': channel_id,
        'start': 0
    }).json()

    assert messages_dict == {
        'messages': [],
        'start': 0,
        'end': -1
    }

    sleep(7)

    messages_dict = requests.get(url + 'channel/messages/v2', params = {
        'token': register_users[0]['token'],
        'channel_id': channel_id,
        'start': 0
    }).json()

    print(message_id_3)
    print(message_id_1)
    print(message_id_2)
    print(messages_dict)
    assert messages_dict == {
        'messages': [
            {
                'message_id': message_id_3,
                'u_id': register_users[0]['auth_user_id'],
                'message': 'hi there',
                'time_created': pytest.approx(now + 5, rel=1),
                'reacts': [],
                'is_pinned': False
            },
            {
                'message_id': message_id_1,
                'u_id': register_users[0]['auth_user_id'],
                'message': 'hi there',
                'time_created': pytest.approx(now + 2, rel=1),
                'reacts': [],
                'is_pinned': False
            },
            {
                'message_id': message_id_2,
                'u_id': register_users[0]['auth_user_id'],
                'message': 'hi there',
                'time_created': pytest.approx(now + 1, rel=1),
                'reacts': [],
                'is_pinned': False
            }
        ],
        'start': 0,
        'end': -1
    }

def test_invalid_channel(register_users):
    
    assert requests.post(url + 'message/sendlater/v1', json={
        'token': register_users[0]['token'],
        'channel_id': 123123,
        'message': 'hi there',
        'time_sent': datetime.utcnow().timestamp() + 2
    }).status_code == 400

def test_msg_length(register_users, channel_factory):
    channel_id = channel_factory(register_users[0]['token'])

    assert requests.post(url + 'message/sendlater/v1', json={
        'token': register_users[0]['token'],
        'channel_id': channel_id,
        'message': 'hi there' * 1000,
        'time_sent': datetime.utcnow().timestamp() + 2
    }).status_code == 400

def test_time_in_past(register_users, channel_factory):
    channel_id = channel_factory(register_users[0]['token'])

    assert requests.post(url + 'message/sendlater/v1', json={
        'token': register_users[0]['token'],
        'channel_id': channel_id,
        'message': 'hi there',
        'time_sent': datetime.utcnow().timestamp() - 2
    }).status_code == 400

def test_channel_valid_user_not_in_channel(register_users, channel_factory):
    channel_id = channel_factory(register_users[0]['token'])

    assert requests.post(url + 'message/sendlater/v1', json={
        'token': register_users[1]['token'],
        'channel_id': channel_id,
        'message': 'hi there',
        'time_sent': datetime.utcnow().timestamp() + 2
    }).status_code == 403

def test_token_invalid(clear, register_users, channel_factory):
    channel_id = channel_factory(register_users[0]['token'])

    assert requests.post(url + 'message/sendlater/v1', json={
        'token': '123123',
        'channel_id': channel_id,
        'message': 'hi there',
        'time_sent': datetime.utcnow().timestamp() + 2
    }).status_code == 403

