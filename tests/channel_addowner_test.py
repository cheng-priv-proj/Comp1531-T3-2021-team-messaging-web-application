import pytest
import requests
import json
import flask
from src import config

import pytest
from src.other import clear_v1

#NEED TO IMPLEMENT CLEAR v2
@pytest.fixture
def clear():
    requests.delete(config.url + "clear/v1")

# Generates new user
@pytest.fixture
def get_valid_token():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
    })
    return response.json()
    
# Generates the first user
@pytest.fixture
def first_register():
    user_details = {
        'email': 'globalowner@test.com',
        'password': 'password', 
        'name_first': 'global',
        'name_last': 'user'
    }
    token_dict = requests.post(url + 'auth/register/v2', json = user_details).json()
    token = token_dict.get('token')
    u_id = token_dict.egt('auth_user_id')

    channel_details = {
        'token': token,
        'name': 'channel',
        'is_public': True
    }
    channel_id_dict = requests.post(url + 'channels/create/v2', json = channel_details).json()
    channel_id = channel_id_dict.get('channel_id')
    
    return {'u_id': u_id, 'token': token, 'channel_id': channel_id}

@pytest.mark.skip
def test_channel_addowner_v1_invalid_channel_id(clear, get_valid_token):
    new_user = get_valid_token()
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': new_user['token'], 'channel_id': -1, 'u_id': new_user['u_id']}).json()

    assert resp.status_code == 400

@pytest.mark.skip
def test_channel_addowner_v1_invalid_u_id(clear, first_register, get_valid_token):
    details = first_register()
    new_user = get_valid_token()
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': new_user['token'], 'channel_id': details['channel_id'], 'u_id': -1}).json()

    assert resp.status_code == 400
@pytest.mark.skip
def test_channel_addowner_v1_user_not_member_of_channel(clear, first_register, get_valid_token):
    details = first_register()
    new_user = get_valid_token()
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': new_user['token'], 'channel_id': details['channel_id'], 'u_id': new_user['u_id']}).json()

    assert resp.status_code == 400
@pytest.mark.skip
def test_channel_addowner_v1_user_already_owner_of_channel(clear, first_register):
    details = first_register()
    requests.post(config.url + 'channel/join/v2', json={'token': details['token'], 'channel_id': details['channel_id']}).json()
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': details['token'], 'channel_id': details['channel_id'], 'u_id': details['u_id']}).json()

    assert resp.status_code == 400
@pytest.mark.skip
def test_channel_addowner_v1_user_without_owner_permissions(clear, first_register):
    # access error
    pass
@pytest.mark.skip
def test_channel_addowner_v1_works(clear, first_register, get_valid_token):
    details = first_register()
    new_user = get_valid_token()
    requests.post(config.url + 'channel/join/v2', json={'token': new_user['token'], 'channel_id': details['channel_id']}).json()
    requests.post(config.url + 'channel/addowner/v1', json={'token': new_user['token'], 'channel_id': details['channel_id'], 'u_id': new_user['u_id']}).json()

    channel_details = requests.post(config.url + 'channel/details/v2', json={'token': new_user['token'], 'channel_id': details['channel_id']}).json()
    assert new_user['u_id'] in channel_details['owner_members']['u_id']