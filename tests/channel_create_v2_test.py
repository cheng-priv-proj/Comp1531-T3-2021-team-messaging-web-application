import pytest
import requests
import json
import flask
from src import config

import pytest
from src.other import clear_v1 

#NEED TO IMPLEMENT CLEAR v2
@pytest.fixture
def clear():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def get_valid_token():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
    })
    token = response.json()
    
    return token['token']

# Tests that a public channel is created correctly.
def test_public_channel_v2(clear, get_valid_token):
    channel_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_valid_token, 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']
    details = requests.get(config.url + 'channel/details/v2', json={'token': get_valid_token, 'channel_id': extracted_channel_id}).json()
    assert details["is_public"] == True

# Tests that a private channel is created correctly.
def test_private_channel_v2(clear, get_valid_token):
    channel_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_valid_token, 'name': 'test channel', 'is_public': False}).json()
    extracted_channel_id = channel_dict['channel_id']
    details = requests.get(config.url + 'channel/details/v2', json={'token': get_valid_token, 'channel_id': extracted_channel_id}).json()
    assert details["is_public"] == False

# Tests that all generated channel id is unique
def test_unique_channel_id_v2(clear, get_valid_token):
    channel_dict1 = requests.post(config.url + 'channels/create/v2', json={'token': get_valid_token, 'name': 'test channel', 'is_public': False}).json()

    extracted_channel_id1 = channel_dict1['channel_id']

    channel_dict2 = requests.post(config.url + 'channels/create/v2', json={'token': get_valid_token, 'name': 'test channel22', 'is_public': False}).json()

    extracted_channel_id2 = channel_dict2['channel_id']

    assert extracted_channel_id2 != extracted_channel_id1

# Testing that the stream owner has correct permissions.
def test_creator_joins_channel_v2(clear):
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'owner@test.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    return_dict = response.json()
    token = return_dict['token']
    auth_user_id = return_dict['auth_user_id']

    channel_dict = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'test channel', 'is_public': False}).json()
    extracted_channel_id = channel_dict['channel_id']
    details = requests.get(config.url + 'channel/details/v2', json={'token': token, 'channel_id': extracted_channel_id}).json()
    assert details["all_members"][auth_user_id]["email"] == "owner@test.com"

def test_becomes_owner_v2(clear):
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'owner@test.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    return_dict = response.json()
    token = return_dict['token']
    auth_user_id = return_dict['auth_user_id']

    channel_dict = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'test channel', 'is_public': False}).json()
    extracted_channel_id = channel_dict['channel_id']
    details = requests.get(config.url + 'channel/details/v2', json={'token': token, 'channel_id': extracted_channel_id}).json()
    assert details["owner_members"][auth_user_id]["email"] == "owner@test.com"

def test_short_channel_name_v2(clear, get_valid_token):
    resp = requests.post(config.url + 'channels/create/v2', json={'token': get_valid_token, 'name': '', 'is_public': False})
    assert(resp.status_code == 400)
    
def test_long_channel_name_v2(clear, get_valid_token):
    resp = requests.post(config.url + 'channels/create/v2', json={'token': get_valid_token, 'name': 'reallylongname1234567eallylongname12345671234567', 'is_public': False})
    assert(resp.status_code == 400)






