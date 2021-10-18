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
from src.data_store import data_store

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
    resp = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'randomtest', 'is_public': True})
    assert(resp.status_code == 403)

# This one should be access error - 
# "AccessError when:"
#        "channel_id is valid and the authorised user is not a member of the channel"

def test_standard_token_invalidation_4(clear_server, get_user_1):

    c_id = requests.post(config.url + 'channels/create/v2', json=
    {
        'token': get_user_1['token'], 
        'name': 'randomtest', 
        'is_public': True
    }).json()

    requests.post(config.url + 'auth/logout/v1', json=
    {
        'token': get_user_1['token']
    }).json()

    resp = requests.get(config.url + 'channel/details/v2', json = {'token': get_user_1['token'], 'channel_id': c_id})
    assert(resp.status_code == 403)

# TEsts the case where one user logs in multiple times
def test_multiple_logins(clear_server, get_user_1):
    token_1 = get_user_1['token']
    token_2  = requests.post(config.url + 'auth/login/v2', json={'email': 'owner@test.com', 'password': 'spotato'}).json().get('token')

    c_id = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'channel', 'is_public': True}).json().get('channel_id')
    requests.post(config.url + 'auth/logout/v1', json={'token': token_1}).json()
    resp_1 = requests.get(config.url + 'channels/listall/v2', json = {'token': token_1})
    assert(resp_1.status_code == 403)

    resp_2 = requests.get(config.url + 'channels/listall/v2', json = {'token': token_2}).json()
    assert resp_2 == { 
        'channels': [
            {
                'channel_id': c_id, 
                'name': 'channel'
            }
        ]
    }

def test_logout_interference(clear_server, get_user_1):
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
    })
    user_2 = response.json()
    requests.post(config.url + 'auth/logout/v1', json=
    {
        'token': get_user_1['token']
    }).json()

    resp = requests.get(config.url + 'channels/listall/v2', json = {'token': user_2['token']})
    assert (resp.status_code != 403)

