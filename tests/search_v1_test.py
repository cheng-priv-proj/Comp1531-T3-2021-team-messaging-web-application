import pytest
import requests
import json
import flask
from requests.models import Response

from src import config
from src.config import url
from src.other import clear_v1
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
        message_id = requests.post(url + 'message/send/v1', json = {
            'token': token,
            'channel_id': channel_id,
            'message': message}).json()
        return message_id
    return send_channel_message
        
@pytest.fixture
def send_message_dm_factory():
    def send_dm(token, dm_id, message):
        message_id = requests.post(url + 'message/senddm/v1', json = {
            'token': token,
            'dm_id': dm_id,
            'message': message}).json()
        return message_id
    return send_dm

def test_search_v1_invalid_token(clear_server):

    response = requests.get(url + 'search/v1', params = {
        'token': -1,
        'query_str': 'hello'
    })

    assert response.status_code == 403

def test_search_v1_query_str_too_short(clear_server, get_valid_token):
    token = get_valid_token['token']

    response = requests.get(url + 'search/v1', params = {
        'token': token,
        'query_str': ''
    })

    assert response.status_code == 400

def test_search_v1_query_str_too_long(clear_server, get_valid_token):
    token = get_valid_token['token']

    response = requests.get(url + 'search/v1', params = {
        'token': token,
        'query_str': 'hello' * 500
    })

    assert response.status_code == 400

def test_search_v1_1_channel(clear_server, get_valid_token, channel_factory, send_message_channel_factory):
    user = get_valid_token
    token = user['token']
    auth_id = user['auth_user_id']
    print(auth_id)
    channel = channel_factory(token, 'channel1')
    print(channel)
    message_id_dict = send_message_channel_factory(token, channel, 'hello')
    message_id = message_id_dict['message_id']
    print(message_id)

    now = datetime.utcnow().timestamp()

    response = requests.get(url + 'search/v1', params = {
        'token': token,
        'query_str': 'hello'
    }).json()

    assert response == {'messages' : [{
        'message_id': message_id, 
        'u_id': auth_id,
        'message': 'hello',
        'time_created': pytest.approx(pytest.approx(now, rel=2)),
        'reacts': [],
        'is_pinned': False
    }]}

def test_search_v1_2_channels(clear_server, get_valid_token, channel_factory, send_message_channel_factory):
    user = get_valid_token
    token = user['token']
    auth_id = user['auth_user_id']
    channel1 = channel_factory(token, 'channel1')
    channel2 = channel_factory(token, 'channel2')

    message_id1 = send_message_channel_factory(token, channel1, 'hello')
    message_id1 = message_id1["message_id"]
    message_id2 = send_message_channel_factory(token, channel2, 'hello')
    message_id2 = message_id2["message_id"]

    now = datetime.utcnow().timestamp()

    response = requests.get(url + 'search/v1', params = {
        'token': token,
        'query_str': 'hello'
    }).json()

    assert response == {'messages' : [{
        'message_id': message_id1,
        'u_id': auth_id,
        'message': 'hello',
        'time_created': pytest.approx(pytest.approx(now, rel=2)),
        'reacts': [],
        'is_pinned': False
    },
    {
        'message_id': message_id2,
        'u_id': auth_id,
        'message': 'hello',
        'time_created': pytest.approx(pytest.approx(now, rel=2)),
        'reacts': [],
        'is_pinned': False
    }]}


def test_search_v1_1_channel_1_dm(clear_server, get_valid_token, channel_factory, dm_factory, send_message_channel_factory, send_message_dm_factory):
    user = get_valid_token
    token = user['token']
    auth_id = user['auth_user_id']
    channel = channel_factory(token, 'channel1')
    dm = dm_factory(token, [auth_id])

    message_id1 = send_message_channel_factory(token, channel, 'hello')
    message_id1 = message_id1["message_id"]
    message_id2 = send_message_dm_factory(token, dm, 'hello')
    message_id2 = message_id2["message_id"]
    print(message_id1)
    print(message_id2)

    now = datetime.utcnow().timestamp()

    response = requests.get(url + 'search/v1', params = {
        'token': token,
        'query_str': 'hello'
    }).json()

    assert response == {'messages' : [{
        'message_id': message_id1,
        'u_id': auth_id,
        'message': 'hello',
        'time_created': pytest.approx(pytest.approx(now, rel=2)),
        'reacts': [],
        'is_pinned': False
    },
    {
        'message_id': message_id2,
        'u_id': auth_id,
        'message': 'hello',
        'time_created': pytest.approx(pytest.approx(now, rel=2)),
        'reacts': [],
        'is_pinned': False
    }]}


def test_search_v1_2_dms(clear_server, get_valid_token, dm_factory, send_message_dm_factory):
    user = get_valid_token
    token = user['token']
    auth_id = user['auth_user_id']

    dm1 = dm_factory(token, [auth_id])
    dm2 = dm_factory(token, [auth_id])

    message_id1 = send_message_dm_factory(token, dm1, 'hello')
    message_id2 = send_message_dm_factory(token, dm2, 'hello')
    message_id1 = message_id1["message_id"]
    message_id2 = message_id2["message_id"]



    now = datetime.utcnow().timestamp()

    response = requests.get(url + 'search/v1', params = {
        'token': token,
        'query_str': 'hello'
    }).json()


    assert response == {'messages' : [{
        'message_id': message_id1,
        'u_id': auth_id,
        'message': 'hello',
        'time_created': pytest.approx(pytest.approx(now, rel=2)),
        'reacts': [],
        'is_pinned': False 
    },
    {
        'message_id': message_id2,
        'u_id': auth_id,
        'message': 'hello',
        'time_created': pytest.approx(pytest.approx(now, rel=2)),
        'reacts': [],
        'is_pinned': False
    }]}

def test_search_v1_query_str_not_found(clear_server, get_valid_token):
    user = get_valid_token
    token = user['token']

    response = requests.get(url + 'search/v1', params = {
        'token': token,
        'query_str': 'hello'
    }).json()

    assert response == {'messages': []}
