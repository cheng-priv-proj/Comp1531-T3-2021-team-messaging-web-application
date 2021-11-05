import pytest
import requests

from src.error import AccessError
from src.config import url

@pytest.fixture
def clear():
    requests.delete(url + 'clear/v1')

# Create an owner and some users
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

def test_standard(register, dm_factory):
    '''
    Tests standard valid case.

    Expects: 
        Correct output from dm_list.
    '''

    dm_id = dm_factory(register[0]['token'], [register[1]['auth_user_id'], register[2]['auth_user_id'], register[3]['auth_user_id']])

    dm_list = requests.get(url + 'dm/list/v1', params = {
        'token': register[0]['token']
        }).json()

    assert dm_list == {
        'dms': [
            {
                'dm_id' : dm_id,
                'name' : 'ownerone, userone, userthree, usertwo'
            }
        ]
    }

def test_creator_only(register, dm_factory):
    '''
    Tests standard valid case when there is only the owner in the dm.

    Expects: 
        Correct output from dm_list.
    '''

    dm_id = dm_factory(register[0]['token'], [])
    
    dm_list = requests.get(url + 'dm/list/v1', params = {
        'token': register[0]['token']
        }).json()

    assert dm_list == {
        'dms': [
            {
                'dm_id' : dm_id,
                'name' : 'ownerone'
            }
        ]
    }

def test_user_has_no_dms(register, dm_factory):
    '''
    Tests case where the user has no dms.

    Expects: 
        Correct output from dm_list.
    '''

    dm_list = requests.get(url + 'dm/list/v1', params = {
        'token': register[0]['token']
        }).json()

    assert dm_list == {
        'dms': []
    }

    dm_factory(register[0]['token'], [register[1]['auth_user_id']])

    dm_list = requests.get(url + 'dm/list/v1', params = {
        'token': register[2]['token']
        }).json()

    assert dm_list == {
        'dms': []
    }

def test_invalid_token():
    '''
    Test expecting access error when token is invalid. 

    Expects: 
        AccessError (403 error)
    '''

    requests.get(url + 'dm/list/v1', params = {
        'token': 'no token has been registered yet'
        }).status_code == 403

