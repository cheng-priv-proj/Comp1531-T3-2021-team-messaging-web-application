import pytest
import requests
import json
import flask
from requests.api import request
from src import config

from src.other import clear_v1
from src.config import url
# Create an owner and some users

@pytest.fixture
def clear_server():
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def register(clear_server):
    owner_id = requests.post(url + 'auth/register/v2', json = {
        'email': 'owner@test.com', 
        'password': 'password', 
        'name_first': 'owner',
        'name_last': 'one' }
        ).json()

    user1_id = requests.post(url + 'auth/register/v2', json = {
        'email': 'user@test.com', 
        'password': 'password', 
        'name_first': 'user',
        'name_last': 'one' }
    ).json()

    user2_id = requests.post(url + 'auth/register/v2', json = {
        'email': 'user2@test.com', 
        'password': 'password', 
        'name_first': 'user',
        'name_last': 'two' }
    ).json()

    user3_id = requests.post(url + 'auth/register/v2', json = {
        'email': 'user3@test.com', 
        'password': 'password', 
        'name_first': 'user',
        'name_last': 'three' }
    ).json()

    return [owner_id, user1_id, user2_id, user3_id]


@pytest.fixture
def dm_factory():
    def create_dm(owner_token, users):
        dm_id = requests.post(url + 'dm/create/v1', json = {
            'token': owner_token,
            'u_ids': users}).json()
        return dm_id['dm_id']
    return create_dm

def test_standard(clear_server, register, dm_factory):
    dm_id = dm_factory(register[0]['token'], [register[1]['auth_user_id'], register[2]['auth_user_id'], register[3]['auth_user_id']])
    
    requests.post(url + 'dm/leave/v1', json = {
        'token': register[1]['token'],
        'dm_id': dm_id
    })

    assert requests.get(url + 'dm/list/v1', json = {
        'token': register[1]['token']
    }).json() == {
        'dms': []
    }

    assert requests.get(url + 'dm/list/v1', json = {
        'token': register[0]['token']
    }).json() == {
        'dms': [
            {
                'dm_id': dm_id,
                'name' :'ownerone, userone, userthree, usertwo'
            }
        ]
    }

def test_creator_leaves(clear_server, register, dm_factory):
    dm_id = dm_factory(register[0]['token'], [register[1]['auth_user_id'], register[2]['auth_user_id'], register[3]['auth_user_id']])
    
    requests.post(url + 'dm/leave/v1', json = {
        'token': register[0]['token'],
        'dm_id': dm_id
    })

    assert requests.get(url + 'dm/list/v1', json = {
        'token': register[0]['token']
    }).json() == {
        'dms':[]
    }

    assert requests.get(url + 'dm/list/v1', json = {
        'token': register[1]['token']
    }).json() == {
        'dms': [
            {
                'dm_id': dm_id,
                'name' :'ownerone, userone, userthree, usertwo'
            }
        ]
    }

def test_invalid_dm_id(clear_server, register):
    assert requests.post(url + 'dm/leave/v1', json = {
        'token': register[1]['token'],
        'dm_id': 1
        }).status_code == 400

def test_invalid_auth_user_id(clear_server, register, dm_factory):

    dm_id = dm_factory(register[0]['token'], [register[1]['auth_user_id']])

    assert requests.post(url + 'dm/leave/v1', json = {
        'token': 'totally a token',
        'dm_id': dm_id
        }).status_code == 403

    assert requests.post(url + 'dm/leave/v1', json = {
        'token': register[2]['token'],
        'dm_id': dm_id
        }).status_code == 403
