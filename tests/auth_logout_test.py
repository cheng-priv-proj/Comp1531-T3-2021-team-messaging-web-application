'''

auth/logout/v1

Given an <<<<active>>> token, invalidates the token to log the user out.

POST

Parameters:{ token }

Return Type:{}

'''

import pytest
import requests
import json
import flask
from src import config

from src.auth import *
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
def auth_id_v2(clear_server):
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    return response.json()

# spec says that the token will be active so there are no excpetional cases

# Test that expects an input error when a logged out user token is used to try and access channel_list_all
# Not sure if return type is access or input error
def test_standard_token_invalidation(clear_server, get_user_1):
    requests.post(config.url + 'auth/logout/v1', json={'token': get_user_1['token']}).json()
    resp = requests.get(config.url + 'channels/listall/v2', json = {'token': get_user_1['token']})
    assert(resp.status_code == 403)

# 
def test_standard_token_invalidation_2(clear_server, get_user_1):
    requests.post(config.url + 'auth/logout/v1', json={'token': get_user_1['token']}).json()
    resp = requests.get(config.url + 'channels/list/v2', json = {'token': get_user_1['token']})
    assert(resp.status_code == 403)


def test_standard_token_invalidation_3(clear_server, get_user_1):
    requests.post(config.url + 'auth/logout/v1', json={'token': get_user_1['token']}).json()
    resp = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'randomtest', 'is_public': True}).json()
    assert(resp.status_code == 403)

# This one should be access error - 
# "AccessError when:"
#        "channel_id is valid and the authorised user is not a member of the channel"

def test_standard_token_invalidation_4(clear_server, get_user_1):
    c_id = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'randomtest', 'is_public': True}).json()
    requests.post(config.url + 'auth/logout/v1', json={'token': get_user_1['token']}).json()

    resp = requests.get(config.url + 'channel/details/v2', json = {'token': get_user_1['token'], 'channel_id': c_id})
    assert(resp.status_code == 403)
