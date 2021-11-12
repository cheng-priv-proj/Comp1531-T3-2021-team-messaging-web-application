import pytest
import requests
from datetime import datetime, timezone
from src import config
from src.config import url

@pytest.fixture
def clear_server():
    '''
    Fixture to reset data store
    '''
    requests.delete(config.url + 'clear/v1')
    pass

@pytest.fixture
def get_valid_token():
    '''
    Registers a user
    '''
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    return response.json()

@pytest.fixture
def register_channel():
    '''
    Fixture that creates a channel
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

@pytest.fixture
def create_standup():
    '''
    Creates a standup
    '''
    def create_standup_function(token, channel_id, length):
        data = requests.post(url + 'standup/start/v1', json = {'token': token, 'channel_id': channel_id, 'length': length})
        return data
    return create_standup_function

@pytest.fixture
def standup_active():
    '''
    Fixture that runs standup active.
    '''
    def standup_active_function(token, channel_id):
        response = requests.get(url + 'standup/active/v1', params = {'token': token, 'channel_id': channel_id})
        return response
    return standup_active_function


def test_standup_active_v1_invalid_channel(clear_server, standup_active, get_valid_token):
    '''
    Test case where channel is invalid.

    Expects:
        InputError (400).
    '''

    token = get_valid_token['token']

    active = standup_active(token, 1)
    assert active.status_code == 400

def test_standup_active_v1_unauthorised_user(clear_server, get_valid_token, register_channel, standup_active):
    '''
    Test case where token is invalid.

    Expects:
        AccessError (403).
    '''

    token1 = get_valid_token['token']
    token2 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'test@gmail.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'}).json()

    channel = register_channel(token1, 'channel1', True)
    active = standup_active(token2['token'], channel)

    assert active.status_code == 403

def test_standup_active_v1_not_active(clear_server, get_valid_token, register_channel, standup_active):
    '''
    Standard test case where standup is not active.

    Expects:
        Correct output from standup/active/v1.
    '''

    token = get_valid_token['token']
    channel = register_channel(token, 'channel1', True)

    active = standup_active(token, channel).json()

    assert active == {
        'is_active': False,
        'time_finish': None
    }

def test_standup_active_v1_active(clear_server, get_valid_token, register_channel, standup_active, create_standup):
    '''
    Standard test.

    Expects:
        Correct output from standup/active/v1.
    '''

    token = get_valid_token['token']
    channel = register_channel(token, 'channel1', True)
    create_standup(token, channel, 1)
    time_finish = int(datetime.now(timezone.utc).timestamp()) + 1
    active = standup_active(token, channel).json()
    assert active == {
        'is_active': True,
        'time_finish': pytest.approx(time_finish, rel=2),
    }