import pytest
import requests
import json
import flask

from src.other import clear_v1
from src.error import InputError

# difficult to test without violating blackbox - only returns dm_id

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


def test_dm_create_v1_invalid_u_id(clear_server):
    with pytest.raises(InputError):
        invalid_auth_ids = ['a', 'b', '-1']
        dm_create_v1(get_valid_token, invalid_auth_ids)

# assumption: dm_ids are generated based on how many already exist
def test_dm_create_v1_returns_id(clear_server):
    valid_auth_ids = ['1', '2', '4', '3']
    dm_id = dm_create_v1(get_valid_token, valid_auth_ids)
    assert dm_id == 1

def test_dm_create_v1_returns_unique_ids(clear_server):
    valid_auth_ids_1 = ['1', '2', '3', '4']
    valid_auth_ids_2 = ['3', '4', '5', '6']
    
    dm_id1 = dm_create_v1(get_valid_token, valid_auth_ids_1)
    dm_id2 = dm_create_v1(get_valid_token, valid_auth_ids_2)
    assert dm_id1 != dm_id2
