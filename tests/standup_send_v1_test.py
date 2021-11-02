import pytest
import requests
from datetime import datetime
from src.config import url

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
        return requests.post(url + 'standup/create/v1', json = {'token': token, 'channel_id': channel_id, 'length': length})
    return create_standup_function

# Sends a standup message
@pytest.fixture
def send_standup_message():
    def send_standup_message_function(token, channel_id, message):
        return requests.post(url + 'standup/send/v1', json = {'token': token, 'channel_id': channel_id, 'message': message})
    return send_standup_message_function

# Gets a channels messages
@pytest.fixture
def get_channel_messages():
    def get_channel_messages_function(token, channel_id, start):
        return requests.get(url + 'channels/messages/v2', params = {'token': token, 'channel_id': channel_id, 'start': start})
    return get_channel_messages_function

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

def test_standup_send_basic_functionality(clear_server, register_user, register_channel, extract_token, create_standup, send_standup_message, get_channel_messages):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    channel_id = register_channel(owner_token, 'channel1', True).json()
    standup_info = create_standup(owner_token, channel_id, 5).json()
    send_standup_message(owner_token, channel_id, 'message1')
    
    messages = get_channel_messages(owner_token, channel_id, 0).json()
    assert messages['messages'][0] ==

def test_standup_send_multiple_messages(clear_server, register_user, register_channel, extract_token, create_standup, send_standup_message, get_channel_messages):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)
    user_info = register_user('user@gmail.com', 'user', 'one')
    user_token = extract_token(user_info)

    channel_id = register_channel(owner_token, 'channel1', True).json()
    requests.post(config.url + 'channel/invite/v2', json={'token': owner_token, 'channel_id': channel_id, 'u_id': user_info['auth_user_id']}).json()

    standup_info = create_standup(owner_token, channel_id, 5).json()
    send_standup_message(owner_token, channel_id, 'message1')
    send_standup_message(user_token, channel_id, 'message2')
    send_standup_message(owner_token, channel_id, 'message3')
    send_standup_message(user_token, channel_id, 'message4')
    
    messages = get_channel_messages(owner_token, channel_id, 0).json()
    assert messages['messages'][0] == 

def test_standup_send_empty_message(clear_server, register_user, register_channel, extract_token, create_standup, send_standup_message, get_channel_messages):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    channel_id = register_channel(owner_token, 'channel1', True).json()
    standup_info = create_standup(owner_token, channel_id, 5).json()
    send_standup_message(owner_token, channel_id, '')
    
    messages = get_channel_messages(owner_token, channel_id, 0).json()
    assert messages['messages'][0] == 
    
def test_standup_send_normal_message_before_standup_over(clear_server, register_user, register_channel, extract_token, create_standup, send_standup_message, get_channel_messages):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    channel_id = register_channel(owner_token, 'channel1', True).json()
    standup_info = create_standup(owner_token, channel_id, 5).json()
    send_standup_message(owner_token, channel_id, '')
    requests.post(url + 'message/send/v1', json = {'token': owner_token, 'channel_id': channel_id, 'message': 'message1'})

    messages = get_channel_messages(owner_token, channel_id, 0).json()
    assert messages['messages'][0] == 

def test_standup_send_tags_in_messsage(clear_server, register_user, register_channel, extract_token, create_standup, send_standup_message, get_channel_messages):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)
    user_info = register_user('user@gmail.com', 'user', 'one')
    user_token = extract_token(user_info)

    channel_id = register_channel(owner_token, 'channel1', True).json()
    requests.post(url + 'channel/invite/v2', json={'token': owner_token, 'channel_id': channel_id, 'u_id': user_info['auth_user_id']}).json()
    standup_info = create_standup(owner_token, channel_id, 5).json()
    send_standup_message(owner_token, channel_id, '@userone')

    assert len(requests.get(url + 'notifications/get/v1', params = {'token': user_token}).json()['notifications']) == 1

def test_standup_send_returns_nothing(clear_server, register_user, register_channel, extract_token, create_standup, send_standup_message, get_channel_messages):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    channel_id = register_channel(owner_token, 'channel1', True).json()
    standup_info = create_standup(owner_token, channel_id, 5).json()
    assert send_standup_message(owner_token, channel_id, 'message1').json == {} 

def test_standup_send_no_active_standup(clear_server, register_user, register_channel, extract_token, create_standup, send_standup_message):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    channel_id = register_channel(owner_token, 'channel1', True).json()
    assert send_standup_message(owner_token, channel_id, 'message1').status_code == 400

def test_standup_send_invalid_message(clear_server, register_user, register_channel, extract_token, create_standup, send_standup_message):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    channel_id = register_channel(owner_token, 'channel1', True).json()
    standup_info = create_standup(owner_token, channel_id, 5).json()
    assert send_standup_message(owner_token, channel_id, '8'*1001).status_code == 400

def test_standup_send_invalid_channel_id(clear_server, register_user, register_channel, extract_token, create_standup, send_standup_message):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)

    send_standup_message(owner_token, 123123123123, 'message1').status_code == 400

def test_standup_send_not_authorized_user(clear_server, register_user, register_channel, extract_token, create_standup, send_standup_message):
    owner_info = register_user('owner@gmail.com', 'owner', 'one')
    owner_token = extract_token(owner_info)
    user_info = register_user('user@gmail.com', 'user', 'one')
    user_token = extract_token(user_info)

    channel_id = register_channel(owner_token, 'channel1', True).json()
    standup_info = create_standup(owner_token, channel_id, 5).json()
    send_standup_message(owner_token, channel_id, 'message1').status_code == 403




