import pytest
import requests
import json
import flask
from requests.models import Response
from src import config

from src.other import clear_v1


@pytest.fixture
def clear_server():
    requests.delete(config.url + "clear/v1")

# Fixture to register someone and returns a dictionary of {token, auth_user_id}
@pytest.fixture
def get_user_1():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'owner@test.com', 
        'password': 'spotato', 
        'name_first': 'owner', 
        'name_last' : 'one'
        })
    return response.json()

# Fixture to register someone and returns a dictionary of {token, auth_user_id}
@pytest.fixture
def auth_id_v2():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    return response.json()

'''
message/edit/v1
Given a message, update its text with new text. 
If the new message is an empty string, the message is deleted.

PUT


Parameters:
    { token, message_id, message }

Return Type:
    {}

InputError when any of:
      
        length of message is over 1000 characters
        message_id does not refer to a valid message within a channel/DM that the authorised user has joined
      
AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:
      
        the message was sent by the authorised user making this request
        the authorised user has owner permissions in the channel/DM
'''

# TO GET MORE COVERAGE, MAYBE DO THE SMAE TESTS WITH THE CHANNELS BUT CHANGE IS_PUBLIC TO PRIVATE and vice versa


def test_normal_case_channel(clear_server, get_user_1, auth_id_v2):
    channel_dict = requests.post(config.url + 'channels/create/v2', json= {
        'token': get_user_1['token'], 
        'name': 'test channel', 
        'is_public': True
    }).json()

    extracted_channel_id = channel_dict['channel_id']
    message_dict = requests.post(config.url + 'message/send/v1', json = {
        'token': get_user_1['token'],
        'channel_id': extracted_channel_id,
        'message': 'Hello there' }).json()

    message_id = message_dict['message_id']

    requests.post(config.url + 'message/edit/v1', json = {
        'token' : get_user_1['token'],
        'message_id': message_id,
        'message' : "GENERAL KENOBI"
    })

    message_dict = requests.get(config.url + 'channel/messages/v2', json = {
        'token': get_user_1['token'],
        'channel_id': extracted_channel_id, 
        'start': 0 }).json()
    messages = message_dict['messages']
    message = messages[0]


    assert message['message'] == "GENERAL KENOBI"

# Over 100 char message
def test_long_edit_channel(clear_server, get_user_1, auth_id_v):
    channel_dict = requests.post(config.url + 'channels/create/v2', json= {
        'token': get_user_1['token'], 
        'name': 'test channel', 
        'is_public': True
    }).json()

    extracted_channel_id = channel_dict['channel_id']
    message_dict = requests.post(config.url + 'message/send/v1', json = {
        'token': get_user_1['token'],
        'channel_id': extracted_channel_id,
        'message': 'Hello there' }).json()

    message_id = message_dict['message_id']

    assert requests.post(config.url + 'message/edit/v1', json = {
        'token' : get_user_1['token'],
        'message_id': message_id,
        'message' : "a" * 1001
    }).status_code == 400

# message edit with empty string 
# same behavoiur as removing
def test_empty_edit_channel(clear_server, get_user_1, auth_id_v):
    channel_dict = requests.post(config.url + 'channels/create/v2', json= {
        'token': get_user_1['token'], 
        'name': 'test channel', 
        'is_public': True
    }).json()

    extracted_channel_id = channel_dict['channel_id']
    message_dict = requests.post(config.url + 'message/send/v1', json = {
        'token': get_user_1['token'],
        'channel_id': extracted_channel_id,
        'message': 'Hello there' }).json()

    message_id = message_dict['message_id']

    message_id = message_dict['message_id']

     requests.post(config.url + 'message/edit/v1', json = {
        'token' : get_user_1['token'],
        'message_id': message_id,
        'message' : "" 
    })


# message_id does not refer to a valid message within a channel/DM that the authorised user has joined