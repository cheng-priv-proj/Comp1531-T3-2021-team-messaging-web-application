import pytest
import requests
import json
import flask
from src import config

import pytest
from src.channels import channels_create_v1
from src.other import clear_v1
from src.channel import channel_details_v1
from src.auth import auth_register_v1

from src.error import AccessError, InputError

# Extracts the auth_user_id from a given dictionary.
@pytest.fixture
def extract_user():
    def extract_user_id_function(auth_user_id_dict):
        return auth_user_id_dict['auth_user_id']
    return extract_user_id_function

# Extracts the channel from a given dictionary.
@pytest.fixture
def extract_channel():
    def extract_channel_id_function(channel_id_dict):
        return channel_id_dict['channel_id']
    return extract_channel_id_function

@pytest.fixture
def clear():
    clear_v1()

# Automatically creates owner user id and channel id. Both are 1 by default.
@pytest.fixture
def register():
    owner_id_dict = auth_register_v1('owner@test.com', 'password', 'owner', 'one')
    owner_user_id = owner_id_dict['auth_user_id']
    channel_id_dict = channels_create_v1(owner_user_id, 'test channel', True)
    return {**owner_id_dict, **channel_id_dict}



@pytest.fixture
def get_valid_token(clear_server):
    response = requests.post(config.url + 'auth/register/v2', data={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    token = response.json()
    return token['token']


# Tests that a public channel is created correctly.
def test_public_channel(get_valid_token):
    channel_dict = requests.post(config.url + 'channels/create/v2', data={'token': get_valid_token, 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    details = requests.get(config.url + 'channel/details/v2', params={'token': get_valid_token, 'name': 'test channel', 'is_public': True}).json()

    assert details["is_public"] == True

# Tests that a private channel is created correctly.
def test_private_channel(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_id = extract_channel(channels_create_v1(auth_user_id, "name", False))
    
    details = channel_details_v1(auth_user_id, channel_id)
    assert details["is_public"] == False

def test_invalid_user_id(clear):
    auth_user_id = 100000
    
    with pytest.raises(AccessError):
        channels_create_v1(auth_user_id, "name", False)

def test_unique_channel_id(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_1 = extract_channel(register)
    channel_2 = extract_channel(channels_create_v1(auth_user_id, "name2", False))

    assert channel_1 != channel_2

# Testing that the stream owner has correct permissions.
def test_creator_joins_channel(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_1 = extract_channel(register)
    
    details = channel_details_v1(auth_user_id, channel_1)
    assert details["all_members"][auth_user_id]["email"] == "owner@test.com"

def test_becomes_owner(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_1 = extract_channel(register)
    
    details = channel_details_v1(auth_user_id, channel_1)
    assert details["owner_members"][auth_user_id]["email"] == "owner@test.com"

def test_short_channel_name(clear, register, extract_user):
    auth_user_id = extract_user(register)
    
    with pytest.raises(InputError):
        channels_create_v1(auth_user_id, "", False)

def test_long_channel_name(clear, register, extract_user):
    auth_user_id = extract_user(register)
    
    with pytest.raises(InputError):
        channels_create_v1(auth_user_id, "reallylongname1234567eallylongname12345671234567", False)

# Test expecting AccessError when both channel name and auth_user_id are invalid.
def test_invalid_user_id_and_invalid_name(clear):
    auth_user_id = 100000
    
    with pytest.raises(AccessError):
        channels_create_v1(auth_user_id, "reallylongname1234567eallylongname12345671234567", False)




