import pytest
import requests
from requests.api import request
from src.config import url

# Fixture to reset data store
@pytest.fixture
def clear():
    requests.delete(url + 'clear/v1')

@pytest.fixture
def register(clear):
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

    return [owner_id, user1_id]

def test_standard(clear, register):
    '''
    Testing standard valid case.

    Expects: 
        Correct output from dm/list.
    '''
    
    dm_id_dict = requests.post(url + 'dm/create/v1', json={
        'token': register[0].get('token'),
        'u_ids': [register[1].get('auth_user_id')]
    }).json()

    requests.delete(url + 'dm/remove/v1', json={
        'token': register[0].get('token'),
        'dm_id': dm_id_dict.get('dm_id')
    })
    
    assert requests.get(url + 'dm/list/v1', params={
        'token': register[0].get('token')
    }).json() == {
        'dms': []
    }

    assert requests.get(url + 'dm/details/v1', params={
        'token': register[0].get('token'),
        'dm_id': dm_id_dict.get('dm_id')
    }).status_code == 403

def test_dm_id_invalid(clear, register):
    '''
    Test expecting input error when dm_id is invalid.

    Expects: 
        InputError (400 error)
    '''

    assert requests.delete(url + 'dm/remove/v1', json={
        'token': register[0].get('token'),
        'dm_id': -123123
    }).status_code == 400

def test_user_not_creator(clear, register):
    '''
    Test expecting Access error when the request is not from the creator.

    Expects: 
        AccessError (403 error)
    '''

    dm_id_dict = requests.post(url + 'dm/create/v1', json={
        'token': register[0].get('token'),
        'u_ids': [register[1].get('auth_user_id')]
    }).json()

    assert requests.delete(url + 'dm/remove/v1', json={
        'token': register[1].get('token'),
        'dm_id': dm_id_dict.get('dm_id')
    }).status_code == 403

def test_token_invalid(clear, register):
    '''
    Test expecting Access error when token is invalid.

    Expects: 
        AccessError (403 error)
    '''
    
    dm_id_dict = requests.post(url + 'dm/create/v1', json={
        'token': register[0].get('token'),
        'u_ids': [register[1].get('auth_user_id')]
    }).json()

    assert requests.delete(url + 'dm/remove/v1', json={
        'token': 'not a valid token',
        'dm_id': dm_id_dict.get('dm_id')
    }).status_code == 403

def test_token_and_dm_id_invalid(clear):
    '''
    Test case where access error is expected to take precedence.

    Expects: 
        AccessError (403 error)
    '''

    assert requests.delete(url + 'dm/remove/v1', json={
        'token': 'not a valid token',
        'dm_id': -123123
    }).status_code == 403