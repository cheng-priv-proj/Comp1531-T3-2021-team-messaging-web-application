import pytest
import requests
import json
import flask
from src import config

from src.other import clear_v1

# Generate invalid tokens some other time

# Fixture to reset data store
@pytest.fixture
def clear():
    clear_v1()

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
        'email': 'user@email.com', 
        'password': 'potato', 
        'name_first': 'a', 
        'name_last' : 'one'
    }).json()
    return response

@pytest.fixture
def user2():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'user2@email.com', 
        'password': 'spotato', 
        'name_first': 'b', 
        'name_last' : 'two'
    }).json()
    return response

@pytest.fixture
def user3():
    response = requests.post(config.url + 'auth/register/v2', json={
            'email': 'user3@email.com',
            'password': 'spotatoo', 
            'name_first': 'c',
            'name_last': 'three',
    }).json()
    return response

# Might add test with valid_u_id some other time too tho
# Test access error priority
def test_invalid_token(clear):
    invalid_token = '-10000'
    invalid_u_id = -10000

    invalid_u_ids = [invalid_u_id]

    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': invalid_token, 
        'u_ids': invalid_u_ids
    })

    assert resp.status_code == 403

# Test Invalid u_id
def test_invalid_u_id(clear, user1, extract_token):
    token1 = extract_token(user1)

    invalid_u_id = -1000
    invalid_u_ids = [invalid_u_id]
    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': invalid_u_ids
    })
    
    assert resp.status_code == 400

# Test multiple Invalid u_id
def test_multiple_invalid_u_ids(clear, user1, user2):
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
    auth1 = extract_id(user1)
    token1 = extract_token(user1)

    u_ids = []

    dm_id = extract_dm(requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': u_ids
    }).json())

    dm_details = requests.get(config.url + 'dm/details/v1', json = {
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

# Test only one person
def test_only_creator_dm(clear, user1, extract_dm, extract_token, extract_id):
    auth1 = extract_id(user1)
    token1 = extract_token(user1)

    u_ids = []

    dm_id = extract_dm(requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': u_ids
    }).json())

    dm_details = requests.get(config.url + 'dm/details/v1', json = {
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

# Test multiple handles
def test_multiple_handles(clear, user1, user2, extract_dm, extract_id, extract_token):
    user1_id = extract_id(user1)
    token1 = extract_token(user1)
    user2_id = extract_id(user2)

    u_ids = [user2_id]

    dm_id = extract_dm(requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': u_ids
    }).json())

    dm_details = requests.get(config.url + 'dm/details/v1', json = {
        'token': token1,
        'dm_id': dm_id
    }).json()
    
    # Find all members
    assert dm_details == {
        'name': 'aone, btwo',
        'members': [
            {
                'u_id': user1_id,
                'email': 'user1@test.com',
                'name_first': 'a',
                'name_last': 'one',
                'handle_str': 'aone'
            },
            {
                'u_id': user2_id,
                'email': 'user2@test.com',
                'name_first': 'b',
                'name_last': 'two',
                'handle_str': 'atwo'
            },
        ]
    }

# Test alphabetically sorted
def test_alphabetically_sorted(clear, user1, user2, user3, extract_dm, extract_id, extract_token):
    user1_id = extract_id(user1)
    token1 = extract_token(user1)
    user2_id = extract_id(user2)
    user3_id = extract_id(user3)

    u_ids = [user2_id, user3]

    dm_id = extract_dm(requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': u_ids
    }).json())

    dm_details = requests.get(config.url + 'dm/details/v1', json = {
        'token': token1,
        'dm_id': dm_id
    }).json()
    
    # Find all members
    assert dm_details == {
        'name': 'aone, btwo, cthree',
        'members': [
            {
                'u_id': user1_id,
                'email': 'user1@test.com',
                'name_first': 'a',
                'name_last': 'one',
                'handle_str': 'aone'
            },
            {
                'u_id': user2_id,
                'email': 'user2@test.com',
                'name_first': 'b',
                'name_last': 'two',
                'handle_str': 'btwo'
            },
            {
                'u_id': user3_id,
                'email': 'user3@test.com',
                'name_first': 'c',
                'name_last': 'three',
                'handle_str': 'cthree'
            },
        ]
    }
