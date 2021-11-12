import pytest
import requests
import json
import flask
from src import config 

from src.other import clear_v1
from src.config import url
from datetime import datetime

@pytest.fixture
def clear_server():
    requests.delete(config.url + "clear/v1")

# Generates new user
@pytest.fixture
def get_valid_token():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
    })
    return response.json()

@pytest.fixture
def channel_factory():
    def create_channel(token, name):
        channel_details = {
            'token': token,
            'name': name,
            'is_public': True
        }
        channel_id_dict = requests.post(url + 'channels/create/v2', json = channel_details).json()
        channel_id = channel_id_dict.get('channel_id')
        return channel_id
    return create_channel

@pytest.fixture
def dm_factory():
    def create_dm(owner_token, users):
        dm_id = requests.post(url + 'dm/create/v1', json = {
            'token': owner_token,
            'u_ids': users}).json()
        return dm_id['dm_id']
    return create_dm

@pytest.fixture
def send_message_channel_factory():
    def send_channel_message(token, channel_id, message):
        requests.post(url + 'message/send/v1', json = {
            'token': token,
            'channel_id': channel_id,
            'message': message}).json()
    return send_channel_message
        
@pytest.fixture
def send_message_dm_factory():
    def send_dm(token, dm_id, message):
        requests.post(url + 'message/senddm/v1', json = {
            'token': token,
            'dm_id': dm_id,
            'message': message}).json()
    return send_dm


def test_user_stats_v1_invalid_token(clear_server):

    response = requests.get(url + 'user/stats/v1', json = {
        'token': -1
    })

    assert response.status_code == 403

def test_user_stats_v1_nothing_joined(clear_server, get_valid_token):
    token = get_valid_token['token']
    now = datetime.utcnow().timestamp()

    response = requests.get(url + 'user/stats/v1', params = {
        'token': token
    }).json()

    assert response == {'user_stats': {
        'channels_joined': [{
            'num_channels_joined': 0,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        }],
        'dms_joined': [{
            'num_dms_joined': 0,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        }],
        'messages_sent': [{
            'num_messages_sent': 0,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        }],
        'involvement_rate': 0
    }}

def test_user_stats_v1_joined_channels(clear_server, get_valid_token, channel_factory, send_message_channel_factory):
    token = get_valid_token['token']
    channel1 = channel_factory(token, 'channel1')
    channel_factory(token, 'channel2')
    send_message_channel_factory(token, channel1, 'hello')

    now = datetime.utcnow().timestamp()

    response = requests.get(url + 'user/stats/v1', params = {
        'token': token
    }).json()

    print(response)

    assert response == {'user_stats': {
        'channels_joined': [
        {
            'num_channels_joined': 0,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        },
        {
            'num_channels_joined': 1,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        },
        {
            'num_channels_joined': 2,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        }],
        'dms_joined': [
        {
            'num_dms_joined': 0,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        }],
        'messages_sent': [
        {
            'num_messages_sent': 0,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        },
        {
            'num_messages_sent': 1,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        }],
        'involvement_rate': 1
    }}


def test_user_stats_v1_joined_dms(clear_server, get_valid_token, dm_factory, send_message_dm_factory):
    user = get_valid_token
    token = user['token']
    dm1 = dm_factory(token, [])
    dm2 = dm_factory(token, [])
    send_message_dm_factory(token, dm1, 'hello')
    send_message_dm_factory(token, dm2, 'abcd')

    now = datetime.utcnow().timestamp()

    response = requests.get(url + 'user/stats/v1', params = {
        'token': token
    }).json()

    assert response == {'user_stats': {
        'channels_joined': [{
            'num_channels_joined': 0,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        }],
        'dms_joined': [
        {
            'num_dms_joined': 0,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        },
        {
            'num_dms_joined': 1,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        },
        {
            'num_dms_joined': 2,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        }],
        'messages_sent': [
        {
            'num_messages_sent': 0,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        },
        {
            'num_messages_sent': 1,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        },
        {
            'num_messages_sent': 2,
            'time_stamp': pytest.approx(pytest.approx(now, rel=2))
        }],
        'involvement_rate': 1
    }}


def test_user_stats_v1_joined_channels_and_dms(clear_server, get_valid_token, channel_factory, send_message_dm_factory, send_message_channel_factory, dm_factory):
    user = get_valid_token
    token = user['token']

    channel1 = channel_factory(token, 'channel1')
    channel_factory(token, 'channel2')
    send_message_channel_factory(token, channel1, 'hello')

    dm1 = dm_factory(token, [])
    dm2 = dm_factory(token, [])
    send_message_dm_factory(token, dm1, 'hello')
    send_message_dm_factory(token, dm2, 'abcd')

    now = datetime.utcnow().timestamp()

    response = requests.get(url + 'user/stats/v1', params = {
        'token': token
    }).json()

    assert response == {'user_stats': {
        'channels_joined': [
        {
            'num_channels_joined': 0,
            'time_stamp': pytest.approx(now, rel=2)
        },
        {
            'num_channels_joined': 1,
            'time_stamp': pytest.approx(now, rel=2)
        },
        {
            'num_channels_joined': 2,
            'time_stamp': pytest.approx(now, rel=2)
        }],
        'dms_joined': [
        {
            'num_dms_joined': 0,
            'time_stamp': pytest.approx(now, rel=2)
        },
        {
            'num_dms_joined': 1,
            'time_stamp': pytest.approx(now, rel=2)
        },
        {
            'num_dms_joined': 2,
            'time_stamp': pytest.approx(now, rel=2)
        }],
        'messages_sent': [
        {
            'num_messages_sent': 0,
            'time_stamp': pytest.approx(now, rel=2)
        },
        {
            'num_messages_sent': 1,
            'time_stamp': pytest.approx(now, rel=2)
        },
        {
            'num_messages_sent': 2,
            'time_stamp': pytest.approx(now, rel=2)
        },
        {
            'num_messages_sent': 3,
            'time_stamp': pytest.approx(now, rel=2)
        }],
        'involvement_rate': 1
    }}



