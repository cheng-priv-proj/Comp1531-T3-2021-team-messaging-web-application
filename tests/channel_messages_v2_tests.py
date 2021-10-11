import pytest

from src.auth import auth_register_v1

from src.channel import channel_messages_v1

from src.channels import channels_create_v1

from src.other import clear_v1

from src.error import InputError
from src.error import AccessError

import pytest
import requests
import json
import flask
from src import config

#NEED TO IMPLEMENT clear for server or change clear v1
@pytest.fixture
def clear_server():
    clear_v1()


@pytest.fixture
def get_user_1():
    response = requests.post(config.url + 'auth/register/v2', data={
        'email': 'owner@test.com', 
        'password': 'spotato', 
        'name_first': 'owner', 
        'name_last' : 'one'
        })
    return response.json()



def test_empty_messages(get_user_1, clear_server):
    
    assert channel_messages_v1(auth_user_id, channel_id, 0) == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

def test_valid_channel_id_and_unauthorized_auth_user_id(clear, register, extract_user, extract_channel):
    channel_id = extract_channel(register)
    invalid_auth_user_id = extract_user(auth_register_v1('test2@gmail.com', '12234234323', 'first', 'last'))
    with pytest.raises(AccessError):
        channel_messages_v1(invalid_auth_user_id, channel_id, 0)

def test_invalid_channel_id(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    invalid_channel_id = 123123123123
    with pytest.raises(InputError):
        channel_messages_v1(auth_user_id, invalid_channel_id, 0)

# Test expecting InputError when given a negative starting index.
def test_negative_start(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_id = extract_channel(register)
    with pytest.raises(InputError):
        channel_messages_v1(auth_user_id, channel_id, -30)

def test_start_greater_than_messages(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_id = extract_channel(register)
    with pytest.raises(InputError):
        channel_messages_v1(auth_user_id, channel_id, 10000)

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

