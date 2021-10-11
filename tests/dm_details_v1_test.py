import pytest
import requests
import json
import flask

from src.other import clear_v1
from src.error import InputError

# Fixture to reset data store
@pytest.fixture
def clear_server():
    #clear_v2()
    pass

@pytest.fixture
def get_valid_token(clear_server):
    response = requests.post(config.url + 'auth/register/v2', data={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    token = response.json()
    return token['token']


def test_dm_details_v1_invalid_dm_id(clear_server):
    with pytest.raises(InputError):
        dm_details(get_valid_token, '-10')
    
def test_dm_details_v1_auth_user_not_member(clear_server):
    user1 = auth_register('email@test.com', 'password', 'firstname', 'lastname')
    user2 = auth_register('email2@test.com', 'password2', 'othername', 'otherlastname')

    dm_id = dm_create_v1(get_valid_token, [user1['auth_user_id'], user2['auth_user_id']])
    with pytest.raises(AccessError):
        dm_details(get_valid_token, dm_id)

def test_dm_details_v1_returns_name(clear_server):
    user1 = auth_register('email@test.com', 'password', 'firstname', 'lastname')
    user2 = auth_register('email2@test.com', 'password2', 'othername', 'otherlastname')
    token = get_valid_token()

    dm_id = dm_create_v1(token, [user1['auth_user_id'], user2['auth_user_id']])
    dm_details = dm_details_v1(token, dm_id)
    assert dm_details['name'] == ['firstnamelastname', 'othernameotherlastname']

def test_dm_details_v1_returns_members(clear_server):
    user1 = auth_register('email@test.com', 'password', 'firstname', 'lastname')
    user2 = auth_register('email2@test.com', 'password2', 'othername', 'otherlastname')
    token = get_valid_token()

    dm_id = dm_create_v1(token, [user1['auth_user_id'], user2['auth_user_id']])
    dm_details = dm_details_v1(token, dm_id)
    #not sure what members is
    assert dm_details['members'] == ''
