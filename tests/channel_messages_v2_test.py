import pytest

from src.other import clear_v1

import pytest
import requests
import json
import flask
from src import config 

# Clear the json.
@pytest.fixture
def clear_server():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def get_user_1():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'owner@test.com', 
        'password': 'spotato', 
        'name_first': 'owner', 
        'name_last' : 'one'
    })
    return response.json()

@pytest.fixture
def get_valid_token():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
    })
    return response.json()


def test_empty_messages(clear_server, get_user_1):
    '''
    Case where no messages are sent

    Expects: 
        Correct output from channel/messages.
    '''
    channel_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    channel_messages = requests.get(config.url + 'channel/messages/v2', params={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'start': 0}).json()
    
    assert channel_messages == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

def test_invalid_channel_id(clear_server, get_user_1):
    '''
    Tests case where channel_id is invalid.

    Expects: 
        InputError (400 error)
    '''
    channel_messages = requests.get(config.url + 'channel/messages/v2', params={'token': get_user_1['token'], 'channel_id': 9912901, 'start': 0})
    assert(channel_messages.status_code == 400)

def test_negative_start(clear_server, get_user_1):
    '''
    Test expecting InputError when given a negative starting index.

    Expects: 
        InputError (400 error)
    '''

    channel_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    channel_messages = requests.get(config.url + 'channel/messages/v2', params={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'start': -42})
    assert(channel_messages.status_code == 400)

def test_start_greater_than_messages(clear_server, get_user_1):
    '''
    Test expecting an error code 400 (input error) when the starting index is greater than the amount of messages avaliable.

    Expects: 
        InputError (400 error)
    '''
    channel_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    channel_messages = requests.get(config.url + 'channel/messages/v2', params={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'start': 10000})
    assert(channel_messages.status_code == 400)

def test_message_is_sent(clear_server, get_user_1):
    '''
    Tests that messages is updated correctly.

    Expects: 
        Correct output from channel/messages.
    '''

    channel_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    requests.post(config.url + 'message/send/v1', json={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'message': "Hello there, General Kenobi"}).json()

    channel_messages = requests.get(config.url + 'channel/messages/v2', params={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'start': 0}).json()
    messages_list = channel_messages['messages']
    specific_message_info = messages_list[0]
    assert specific_message_info['message'] == "Hello there, General Kenobi"
    assert channel_messages['start'] == 0
    assert channel_messages['end'] == -1

def test_user_not_member_of_channel(clear_server, get_user_1, get_valid_token):
    '''
    Test case where user is not a member of the channel.

    Expects: 
        AccessError (403 error)
    '''

    channel_dict = requests.post(config.url + 'channels/create/v2', json={
        'token': get_user_1['token'], 
        'name': 'test channel', 
        'is_public': True
    }).json()
    extracted_channel_id = channel_dict['channel_id']

    token2 = get_valid_token['token']
    
    assert requests.get(config.url + 'channel/messages/v2', params={
        'token': token2, 
        'channel_id': extracted_channel_id, 
        'start': 0
    }).status_code == 403

def test_long(clear_server, get_user_1):
    '''
    Test standard case but with more than 50 messages. 

    Expects: 
        Correct output from channel/messages.
    '''

    channel_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    for _ in range(51):
        requests.post(config.url + 'message/send/v1', json={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'message': "Hello there, General Kenobi"}).json()

    channel_messages = requests.get(config.url + 'channel/messages/v2', params={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'start': 0}).json()
    messages_list = channel_messages['messages']
    for specific_message_info in messages_list:

        assert specific_message_info['message'] == "Hello there, General Kenobi"

    assert channel_messages['start'] == 0
    assert channel_messages['end'] == 50