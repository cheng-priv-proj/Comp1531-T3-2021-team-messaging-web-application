import pytest
import requests
from datetime import datetime

from src.config import url

'''
message/react/v1
Given a message within a channel or DM the authorised user is part of, add a "react" to that particular message.

POST

Parameters:{ token, message_id, react_id }

Return Type:{}


InputError when any of:
      
        message_id is not a valid message within a channel or DM that the authorised user has joined
        react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1
        the message already contains a react with ID react_id from the authorised user
'''

# Extracts the token from a given dictionary.
@pytest.fixture
def extract_token():
    def extract_token_id_function(auth_user_id_dict):
        return auth_user_id_dict['token']
    return extract_token_id_function

# Extracts the auth_user_id from a given dictionary.
@pytest.fixture
def extract_user():
    def extract_auth_user_id_function(auth_user_id_dict):
        return auth_user_id_dict['auth_user_id']
    return extract_auth_user_id_function

# Extracts the channel from a given dictionary.
@pytest.fixture
def extract_channel():
    def extract_channel_id_function(channel_id_dict):
        return channel_id_dict['channel_id']
    return extract_channel_id_function

# Extracts the message from a given dictionary
@pytest.fixture
def extract_message():
    def extract_message_id_function(message_id_dict):
        return message_id_dict['message_id']
    return extract_message_id_function

@pytest.fixture
def clear():
    requests.delete(url + 'clear/v1')

# Automatically create owner user id and channel id. Both are 1 by default.
@pytest.fixture
def register():
    owner_id_dict = requests.post(url + 'auth/register/v2', json = {
        'email': 'owner@test.com', 
        'password': 'password', 
        'name_first': 'owner',
        'name_last': 'one' }
        ).json()
    owner_user_token = owner_id_dict['token']
    channel_id_dict = requests.post(url + 'channels/create/v2', json = {
        'token': owner_user_token,
        'name': 'channel_name', 
        'is_public': True }).json()

    return {**owner_id_dict, **channel_id_dict}

@pytest.fixture
def get_user_1():
    response = requests.post(url + 'auth/register/v2', json={
        'email': 'owner@test.com', 
        'password': 'spotato', 
        'name_first': 'owner', 
        'name_last' : 'one'
        })
    return response.json()

@pytest.fixture
def auth_id_v2():
    response = requests.post(url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    return response.json()

def test_react_own(clear, register, extract_token, extract_user, extract_channel, extract_message):
    '''
    Standard test with one message. (The person reacts to their own message)

    Expects: 
        Correct output from channel/messages.
    '''

    channel_id = extract_channel(register)
    owner_token = extract_token(register)

    message_id = requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' }).json()

    requests.post(url + 'message/react/v1', json = {
        'token': owner_token,
        'message_id': extract_message(message_id),
        'react_id': 1 }).json()
    
    messages = requests.get(url + 'channel/messages/v2', params = {
        'token': owner_token,
        'channel_id': channel_id, 
        'start': 0 }).json()

    messages = messages['messages']
    reacts = messages[0]['reacts']

    assert reacts == [{
        'react_id' : 1,
        'u_ids' : [extract_user(register)],
        'is_this_user_reacted' : True
    }]

def test_react_not_own(clear, register, extract_token, extract_user, extract_channel, extract_message, auth_id_v2):
    '''
    Standard test with one message. (The person reacts does not react to their own message)

    Expects: 
        Correct output from channel/messages.
    '''

    channel_id = extract_channel(register)
    owner_token = extract_token(register)

    requests.post(url + 'channel/join/v2', json = {'token': auth_id_v2['token'],'channel_id': channel_id})

    message_id = requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' }).json()

    requests.post(url + 'message/react/v1', json = {
        'token': auth_id_v2['token'],
        'message_id': extract_message(message_id),
        'react_id': 1 }).json()
    
    messages = requests.get(url + 'channel/messages/v2', params = {
        'token': owner_token,
        'channel_id': channel_id, 
        'start': 0 }).json()

    messages = messages['messages']
    reacts = messages['reacts']

    assert reacts == [{
        'react_id' : 1,
        'u_ids' : [auth_id_v2['token']],
        'is_this_user_reacted' : False
    }]

def test_invalid_message_id(clear, register, extract_token, extract_user, extract_channel, extract_message, auth_id_v2):
    '''
    message_id is not a valid message within a channel or DM that the authorised user has joined

    Expects: 
        InputError
    '''

    channel_id = extract_channel(register)
    owner_token = extract_token(register)

    requests.post(url + 'channel/join/v2', json = {'token': auth_id_v2['token'],'channel_id': channel_id})

    requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' }).json()

    assert requests.post(url + 'message/react/v1', json = {
        'token': auth_id_v2['token'],
        'message_id': 69696969,
        'react_id': 1 }).status_code == 400
    

def test_invalid_react_id(clear, register, extract_token, extract_user, extract_channel, extract_message, auth_id_v2):
    '''
    Invalid React id

    Expects: 
        InputError
    '''

    channel_id = extract_channel(register)
    owner_token = extract_token(register)

    requests.post(url + 'channel/join/v2', json = {'token': auth_id_v2['token'],'channel_id': channel_id})

    message_id = requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' }).json()

    assert requests.post(url + 'message/react/v1', json = {
        'token': auth_id_v2['token'],
        'message_id': extract_message(message_id),
        'react_id': 420}).status_code == 400


def test_already_reacted_id(clear, register, extract_token, extract_user, extract_channel, extract_message, auth_id_v2):
    '''
    Invalid React id

    Expects: 
        InputError
    '''

    channel_id = extract_channel(register)
    owner_token = extract_token(register)

    requests.post(url + 'channel/join/v2', json = {'token': auth_id_v2['token'],'channel_id': channel_id})

    message_id = requests.post(url + 'message/send/v1', json = {
        'token': owner_token,
        'channel_id': channel_id,
        'message': 'testmessage' }).json()

    requests.post(url + 'message/react/v1', json = {
        'token': auth_id_v2['token'],
        'message_id': extract_message(message_id),
        'react_id': 1})

    assert requests.post(url + 'message/react/v1', json = {
        'token': auth_id_v2['token'],
        'message_id': extract_message(message_id),
        'react_id': 1}).status_code == 400


def test_react_own_dm(clear, get_user_1, auth_id_v2, extract_message):
    '''
    Standard test with one message. (The person reacts to their own message)

    Expects: 
        Correct output from channel/messages.
    '''

    dm_id = requests.post(url + 'dm/create/v1', json = {
        'token': get_user_1['token'],
        'u_ids': [auth_id_v2['auth_user_id']]}).json()

    dm_id = dm_id['dm_id']

    message_id = requests.post(url + 'message/senddm/v1', json = {
        'token': get_user_1['token'],
        'dm_id': dm_id,
        'message': 'HELLO THERE GENERAL KENOBI' }).json()

    requests.post(url + 'message/react/v1', json = {
        'token': get_user_1['token'],
        'message_id': extract_message(message_id),
        'react_id': 1 }).json()
    
    messages = requests.get(url + 'dm/messages/v1', params = {
        'token': get_user_1['token'],
        'dm_id': dm_id, 
        'start': 0 }).json()

    messages = messages['messages']
    reacts = messages['reacts']

    assert reacts == [{
        'react_id' : 1,
        'u_ids' : [get_user_1['auth_user_id']],
        'is_this_user_reacted' : True
    }]


def test_react_not_own_dm(clear, get_user_1, auth_id_v2, extract_message):
    '''
    Standard test with one message. (The person reacts does not react to their own message)

    Expects: 
        Correct output from channel/messages.
    '''

    dm_id = requests.post(url + 'dm/create/v1', json = {
        'token': get_user_1['token'],
        'u_ids': [auth_id_v2['auth_user_id']]}).json()

    dm_id = dm_id['dm_id']

    message_id = requests.post(url + 'message/senddm/v1', json = {
        'token': get_user_1['token'],
        'dm_id': dm_id,
        'message': 'HELLO THERE GENERAL KENOBI' }).json()

    requests.post(url + 'message/react/v1', json = {
        'token': auth_id_v2['token'],
        'message_id': extract_message(message_id),
        'react_id': 1 }).json()
    
    messages = requests.get(url + 'dm/messages/v1', params = {
        'token': get_user_1['token'],
        'dm_id': dm_id, 
        'start': 0 }).json()

    messages = messages['messages']
    reacts = messages['reacts']

    assert reacts == [{
        'react_id' : 1,
        'u_ids' : [auth_id_v2['token']],
        'is_this_user_reacted' : False
    }]