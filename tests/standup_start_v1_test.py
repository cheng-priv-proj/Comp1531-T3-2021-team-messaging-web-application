import pytest
import requests
from datetime import datetime
from src.config import url
from time import sleep

@pytest.fixture
def clear_server():
    requests.delete(url + "clear/v1")

# Extracts the token from a given dictionary.
@pytest.fixture
def extract_token():
    def extract_token_id_function(token_dict):
        return token_dict['token']
    return extract_token_id_function

# Registers an user and returns their registration info, auth_id and token and handle_str
# Assumes handle_str does not require additional processing past concatenation
@pytest.fixture
def register_user():
    def register_user_function(email, name_first, name_last):
        registration_info = {
            'email': email, 
            'password': 'password', 
            'name_first': name_first,
            'name_last': name_last }
        owner_id_dict = requests.post(url + 'auth/register/v2', json = registration_info).json()
        
        owner_id_dict['handle_str'] = registration_info.get('name_first') + registration_info.get('name_last')
        return {**owner_id_dict, **registration_info}
    return register_user_function

# Creates a standup
@pytest.fixture
def create_standup():
    def create_standup_function(token, channel_id, length):
        return requests.post(url + 'standup/start/v1', json = {'token': token, 'channel_id': channel_id, 'length': length})
    return create_standup_function

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

def test_create_standup_basic_functionality(clear_server, register_channel, register_user, create_standup, extract_token):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    channel_id = register_channel(owner_token, 'channel1', True)
    standup_info = create_standup(owner_token, channel_id, 5).json()


    now = datetime.now().timestamp()        
    assert standup_info['time_finish'] == pytest.approx(now + 5, rel=2)

    sleep(5)

def test_create_standup_no_second_standup(clear_server, register_channel, register_user, create_standup, extract_token):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    channel_id = register_channel(owner_token, 'channel1', True)
    create_standup(owner_token, channel_id, 5).json()
    error = create_standup(owner_token, channel_id, 5).status_code

    assert error == 400

def test_create_standup_invalid_channel_id(clear_server, register_user, create_standup, extract_token):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    error = create_standup(owner_token, 12312, 5).status_code

    assert error == 400

def test_create_standup_negative_length(clear_server, register_channel, register_user, create_standup, extract_token):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    channel_id = register_channel(owner_token, 'channel1', True)
    error = create_standup(owner_token, channel_id, -5).status_code
    
    assert error == 400

def test_create_standup_unauthorized_member(clear_server, register_channel, register_user, create_standup, extract_token):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    user_info = register_user('user@gmail.com', 'user', 'one')
    channel_id = register_channel(owner_token, 'channel1', False)
    error = create_standup(extract_token(user_info), channel_id, 5).status_code

    assert error == 403

def test_create_priority_error(clear_server, register_channel, register_user, create_standup, extract_token):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    user_info = register_user('user@gmail.com', 'user', 'one')
    channel_id = register_channel(owner_token, 'channel1', False)
    create_standup(owner_token, channel_id, 5).json()
    error = create_standup(extract_token(user_info), channel_id, -5).status_code

    assert error == 403

def test_multiple_standups(clear_server, register_channel, register_user, create_standup, extract_token):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    channel_id1 = register_channel(owner_token, 'channel1', False)
    channel_id2 = register_channel(owner_token, 'channel2', False)
    standup_id1 = create_standup(owner_token, channel_id1, 5).json()
    standup_id2 = create_standup(owner_token, channel_id2, 5).json()
    now = datetime.now().timestamp()

    assert standup_id1['time_finish'] == pytest.approx(now + 5, rel=2)
    assert standup_id2['time_finish'] == pytest.approx(now + 5, rel=2)