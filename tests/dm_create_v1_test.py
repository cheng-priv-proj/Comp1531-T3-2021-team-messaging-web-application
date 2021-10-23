import pytest
import requests
from src import config

# Fixture to reset data store
@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

# Extracts the dm_id from a dictionary
@pytest.fixture 
def extract_dm():
    def extract_dm_function(dm_id_dict):
        return dm_id_dict.get('dm_id')
    return extract_dm_function

# Extract token from channel details
@pytest.fixture
def extract_token():
    def extract_token_function(auth_details):
        return auth_details.get('token')
    return extract_token_function

# Extract id from channel details
@pytest.fixture
def extract_id():
    def extract_token_function(auth_details):
        return auth_details.get('auth_user_id')
    return extract_token_function

# Fixture to register someone and returns a dictionary of {token, auth_user_id}
@pytest.fixture
def user1():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'user1@test.com', 
        'password': 'potato', 
        'name_first': 'a', 
        'name_last' : 'one'
    }).json()
    return response

@pytest.fixture
def user2():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'user2@test.com', 
        'password': 'spotato', 
        'name_first': 'b', 
        'name_last' : 'two'
    }).json()
    return response

@pytest.fixture
def user3():
    response = requests.post(config.url + 'auth/register/v2', json={
            'email': 'user3@test.com',
            'password': 'spotatoo', 
            'name_first': 'c',
            'name_last': 'three',
    }).json()
    return response

def test_invalid_token(clear):
    '''
    Test that access error has priority

    Expects: 
        AccessError (403 error)
    '''

    invalid_token = '-10000'
    invalid_u_id = -10000

    invalid_u_ids = [invalid_u_id]

    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': invalid_token, 
        'u_ids': invalid_u_ids
    })

    assert resp.status_code == 403

def test_invalid_u_id(clear, user1, extract_token):
    '''
    Test Invalid u_id

    Expects: 
        InputError (400 error)
    '''

    token1 = extract_token(user1)

    invalid_u_id = -1000
    invalid_u_ids = [invalid_u_id]
    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': invalid_u_ids
    })

    assert resp.status_code == 400

def test_multiple_invalid_u_ids(clear, user1, user2, extract_token, extract_id):
    '''
    Test multiple Invalid u_id

    Expects: 
        InputError (400 error)
    '''

    token1 = extract_token(user1)

    invalid_u_id1 = -1000
    valid_u_id2 = extract_id(user2)

    invalid_u_ids = [invalid_u_id1, valid_u_id2]

    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': invalid_u_ids
    })
    
    assert resp.status_code == 400

def test_dm_id_correct(clear, user1, extract_dm, extract_token, extract_id):
    '''
    Tests that the dm_id generated is correct.

    Expects: 
        Correct output from dm_details.
    '''

    auth1 = extract_id(user1)
    token1 = extract_token(user1)

    u_ids = []

    dm_id = extract_dm(requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': u_ids
    }).json())

    dm_details = requests.get(config.url + 'dm/details/v1', params = {
        'token': token1,
        'dm_id': dm_id
    }).json()
    
    # Find all members
    assert dm_details == {
        'name': 'aone',
        'members': [
            {
                'u_id': auth1,
                'email': 'user1@test.com',
                'name_first': 'a',
                'name_last': 'one',
                'handle_str': 'aone'
            }
        ]
    }

def test_only_creator_dm(clear, user1, extract_dm, extract_token, extract_id):
    '''
    Test case where there is only one person.

    Expects: 
        Correct output from dm_details.
    '''
    auth1 = extract_id(user1)
    token1 = extract_token(user1)

    u_ids = []

    dm_id = extract_dm(requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': u_ids
    }).json())

    dm_details = requests.get(config.url + 'dm/details/v1', params = {
        'token': token1,
        'dm_id': dm_id
    }).json()
    
    # Find all members
    assert dm_details == {
        'name': 'aone',
        'members': [
            {
                'u_id': auth1,
                'email': 'user1@test.com',
                'name_first': 'a',
                'name_last': 'one',
                'handle_str': 'aone'
            }
        ]
    }

def test_multiple_handles(clear, user1, user2, extract_dm, extract_id, extract_token):
    '''
    Test case where there are multiple handles.

    Expects: 
        Correct output from dm_details.
    '''

    user1_id = extract_id(user1)
    token1 = extract_token(user1)
    user2_id = extract_id(user2)

    u_ids = [user2_id]

    dm_id = extract_dm(requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': u_ids
    }).json())

    dm_details = requests.get(config.url + 'dm/details/v1', params = {
        'token': token1,
        'dm_id': dm_id
    }).json()
    
    # Find all members
    assert dm_details == {
        'name': 'aone, btwo',
        'members': [
            {
                'u_id': user2_id,
                'email': 'user2@test.com',
                'name_first': 'b',
                'name_last': 'two',
                'handle_str': 'btwo'
            },
            {
                'u_id': user1_id,
                'email': 'user1@test.com',
                'name_first': 'a',
                'name_last': 'one',
                'handle_str': 'aone'
            },
        ]
    }

def test_name_alphabetically_sorted(clear, user1, user2, user3, extract_dm, extract_id, extract_token):
    '''
    Test alphabetically sorted

    Expects: 
        Correct output from dm/details.
    '''

    extract_id(user1)
    token1 = extract_token(user1)
    user2_id = extract_id(user2)
    user3_id = extract_id(user3)

    u_ids = [user2_id, user3_id]

    dm_id = extract_dm(requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': u_ids
    }).json())

    dm_details = requests.get(config.url + 'dm/details/v1', params = {
        'token': token1,
        'dm_id': dm_id
    }).json()
    
    # Find all members
    assert dm_details['name'] == 'aone, btwo, cthree'
