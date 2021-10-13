import pytest

from src.other import clear_v1

import pytest
import requests
import json
import flask
from src import config

#NEED TO IMPLEMENT clear for server or change clear v1
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


# No messages are sent
def test_empty_messages(get_user_1, clear_server):
    channel_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    channel_messages = requests.get(config.url + 'channel/messages/v2', json={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'start': 0})
    
    assert channel_messages == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

''' Auth id is not a parameter yet the spec still considers it so. Need to clarify what it means 
it says in the spec:
"return access error when,"
'channel_id is valid and the authorised user is not a member of the channel'


def test_valid_channel_id_and_unauthorized_auth_user_id(clear, register, extract_user, extract_channel):
    channel_id = extract_channel(register)
    invalid_auth_user_id = extract_user(auth_register_v1('test2@gmail.com', '12234234323', 'first', 'last'))
    with pytest.raises(AccessError):
        channel_messages_v1(invalid_auth_user_id, channel_id, 0)

'''
def test_invalid_channel_id(get_user_1, clear_server):
    channel_messages = requests.get(config.url + 'channel/messages/v2', json={'token': get_user_1['token'], 'channel_id': 9912901, 'start': 0}).json()
    assert(channel_messages.status_code == 400)

# Test expecting InputError when given a negative starting index.
def test_negative_start(get_user_1, clear_server):

    channel_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    channel_messages = requests.get(config.url + 'channel/messages/v2', json={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'start': -42}).json()
    assert(channel_messages.status_code == 400)

# Test expecting an error code 400 (input error) when the starting index is greater than the amount of messages avaliable.
def test_start_greater_than_messages(get_user_1, clear_server):
    channel_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    channel_messages = requests.get(config.url + 'channel/messages/v2', json={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'start': 10000}).json()
    assert(channel_messages.status_code == 400)

# ASSUMES THAT message/send/v1 COMPLETELY WORKS
@pytest.mark.skip('Messages send not yet implemented')
def test_message_is_sent(clear_server, get_user_1):
    channel_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    requests.post(config.url + 'message/send/v1', json={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'message': "Hello there, General Kenobi"}).json()

    channel_messages = requests.get(config.url + 'channel/messages/v2', json={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'start': 0}).json()
    messages_list = channel_messages['messages']
    specific_message_info = messages_list[0]
    assert specific_message_info['message'] == "Hello there, General Kenobi"
    assert channel_messages['start'] == 0
    assert channel_messages['end'] == -1

@pytest.mark.skip('Not implemented')
def test_message_is_edited():
    return


''' Auth id is not a parameter yet the spec still considers it so. Need to clarify what it means 
it says in the spec:
"return access error when,"
'channel_id is valid and the authorised user is not a member of the channel'


# Test that expects AccessError priority when both message index and auth id are invalid.
def test_start_greater_than_messages_and_invalid_auth_id(clear, register, extract_channel):
    invalid_auth_user_id = 100
    channel_id = extract_channel(register)
    with pytest.raises(AccessError):
        channel_messages_v1(invalid_auth_user_id, channel_id, 10000)

# Test that expects AccessError priority when both channel and auth id are invalid.
def test_invalid_channel_id_and_unauthorized_user(clear):
    with pytest.raises(AccessError):
        channel_messages_v1(123123123, 12312312345, 0)

def test_invalid_auth_user_id(clear, register, extract_channel):
    channel_id = extract_channel(register)
    with pytest.raises(AccessError):
        channel_messages_v1(21312123, channel_id, 0)


'''
