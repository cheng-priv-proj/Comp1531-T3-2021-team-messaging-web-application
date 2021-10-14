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

# Fixture to register someone and returns a dictionary of {token, auth_user_id}
@pytest.fixture
def token1():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'apple', 
        'name_last' : 'one'
    }).json()
    return response.get('token')

@pytest.fixture
def token2():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'owner@test.com', 
        'password': 'spotato', 
        'name_first': 'banana', 
        'name_last' : 'two'
    }).json()
    return response.get('token')

@pytest.fixture
def token3():
    response = requests.post(config.url + 'auth/register/v2', json={
            'email': 'eexample@email.com',
            'password': 'spotatoo', 
            'name_first': 'crabapple',
            'name_last': 'three',
    }).json()
    return response.get('token')

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
def test_invalid_u_id(clear, token1):
    invalid_u_id = -1000
    invalid_u_ids = [invalid_u_id]
    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': invalid_u_ids
    })
    
    assert resp.status_code == 400

# Test multiple Invalid u_id
def test_multiple_invalid_u_ids(clear, token1):
    invalid_u_id1 = -1000
    invalid_u_id2 = -2000
    invalid_u_ids = [invalid_u_id1, invalid_u_id2]
    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': invalid_u_ids
    })
    
    assert resp.status_code == 400

# Test only one person
def test_only_creator_dm(clear, token1, extract_dm):
    u_ids = []

    dm_id = extract_dm(requests.post(config.url + 'dm/create/v1', json={
        'token': token1, 
        'u_ids': u_ids
    }).json())

    dm_details = requests.get(config.url + 'dm/details/v1', json = {
        'token': token1,
        'dm_id': dm_id
    }).json()

    assert dm_details == {
        'name': 'appleone',
        'members': 'Start here' # This isn't finished go from here
    }

# Test returns correct dm_id
def test_returns_id(clear, get_valid_token, get_valid_token_2, get_valid_token_3):
    auth_ids = [get_valid_token['auth_user_id'], get_valid_token_2['auth_user_id']]
    resp = requests.post(config.url + 'dm/create/v1', json={'token': get_valid_token_3['token'], 'u_ids': auth_ids}).json()

    assert resp['dm_id'] == 1

# Test create multiple dm
def test_returns_unique_ids(clear, get_valid_token, get_valid_token_2, get_valid_token_3):
    user1 = get_valid_token['auth_user_id']
    user2 = get_valid_token_2['auth_user_id']
    user3 = get_valid_token_3['auth_user_id']
    
    resp1 = requests.post(config.url + 'dm/create/v1', json={'token': user1['token'], 'u_ids': [user2, user3]}).json()
    resp2 = requests.post(config.url + 'dm/create/v1', json={'token': user3['token'], 'u_ids': [user1, user2]}).json()

    assert resp1['dm_id'] != resp2['dm_id']

# Test create dm name
def test_name(clear, get_valid_token, get_valid_token_2, get_valid_token_3):
    auth_ids = [get_valid_token['auth_user_id'], get_valid_token_2['auth_user_id']]

    resp = requests.post(config.url + 'dm/create/v1', json={'token': get_valid_token_3['token'], 'u_ids': auth_ids}).json()
    resp_details = requests.get(config.url + 'dm/details/v1', json={'token': get_valid_token_3, 'dm_id': resp['dm_id']}).json()

    assert resp_details['name'] == ['Johnsmith', 'ownerone']

def test_members(clear, get_valid_token, get_valid_token_2, get_valid_token_3):
    auth_ids = [get_valid_token['auth_user_id'], get_valid_token_2['auth_user_id']]
    resp = requests.post(config.url + 'dm/create/v1', json={'token': get_valid_token_3['token'], 'u_ids': auth_ids}).json()
    resp_details = requests.get(config.url + 'dm/details/v1', json={'token': get_valid_token_3, 'dm_id': resp['dm_id']}).json()

    #not sure what members looks like
    assert resp_details['members'] == ''

# Test multiple handles

# Test alphabetically sorted

# Test owner created (Not yet implemented)