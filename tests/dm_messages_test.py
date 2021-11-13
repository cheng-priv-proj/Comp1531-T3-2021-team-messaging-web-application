import pytest
import requests

from src.config import url

@pytest.fixture
def clear():
    '''
    Clears the datastore.
    '''
    requests.delete(url + 'clear/v1')

@pytest.fixture
def register(clear):
    '''
    Create an owner and some users
    '''
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
        'email': 'user@test.com', 
        'password': 'password', 
        'name_first': 'user',
        'name_last': 'two' }
    ).json()

    user3_id = requests.post(url + 'auth/register/v2', json = {
        'email': 'user@test.com', 
        'password': 'password', 
        'name_first': 'user',
        'name_last': 'three' }
    ).json()

    return [owner_id, user1_id, user2_id, user3_id]


@pytest.fixture
def dm_factory():
    '''
    Fixture that creates dms.
    '''
    def create_dm(owner_token, users):
        dm_id = requests.post(url + 'dm/create/v1', json = {
            'token': owner_token,
            'u_ids': users}).json()
        return dm_id['dm_id']
    return create_dm

def test_no_messages(register, dm_factory):
    '''
    Test case where there are no messages.

    Expects: 
        Correct output from dm/messages.
    '''

    dm_id = dm_factory(register[0]['token'], [])

    messages_dict = requests.get(url + 'dm/messages/v1', params = {
        'token': register[0]['token'],
        'dm_id': dm_id,
        'start': 0
    }).json()

    assert messages_dict == {
        'messages': [],
        'start': 0,
        'end': -1
    }

def test_invalid_token_valid_dm_id(register, dm_factory):
    '''
    Test expecting access error when token and dm_id is invalid.

    Expects: 
        AccessError (403 error)
    '''

    dm_id = dm_factory(register[0]['token'], [])

    assert requests.get(url + 'dm/messages/v1', params = {
        'token': register[1]['token'],
        'dm_id': dm_id,
        'start': 0
    }).status_code == 403

def test_invalid_dm_id(register):
    '''
    Test expecting input error when dm_id is invalid.

    Expects: 
        InputError (400 error)
    '''

    assert requests.get(url + 'dm/messages/v1', params = {
        'token': register[0]['token'],
        'dm_id': 0,
        'start': 0
    }).status_code == 400

def test_invalid_start(register, dm_factory):
    '''
    Test expecting input error when start is invalid.

    Expects: 
        InputError (400 error)
    '''

    dm_id = dm_factory(register[0]['token'], [])

    assert requests.get(url + 'dm/messages/v1', params = {
        'token': register[0]['token'],
        'dm_id': dm_id,
        'start': 50
    }).status_code == 400

def test_negative_start(register, dm_factory):
    '''
    Test expecting input error when start is invalid.

    Expects: 
        InputError (400 error)
    '''

    dm_id = dm_factory(register[0]['token'], [])

    assert requests.get(url + 'dm/messages/v1', params = {
        'token': register[0]['token'],
        'dm_id': dm_id,
        'start': -1
    }).status_code == 400
    pass

def test_invalid_dm_and_token(clear):
    '''
    Test expecting Acccess error when token and dm is invalid.

    Expects: 
        AccessError (403 error)
    '''

    assert requests.get(url + 'dm/messages/v1', params = {
        'token': 'no token has been registered',
        'dm_id': 1,
        'start': 0
    }).status_code == 403
