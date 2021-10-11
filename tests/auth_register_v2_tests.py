import pytest
import requests
import json
import flask
from requests.models import Response
from src import config

from src.auth import *
from src.error import InputError
from src.other import clear_v2

from src.auth import *
from src.other import clear_v1
from src.channel import channel_details_v1
from src.channels import channels_create_v1

#NEED TO IMPLEMENT CLEAR v2 or change clear v1
@pytest.fixture
def clear_server():
    clear_v2()

# Fixture to register someone and returns a dictionary of {token, auth_user_id}
@pytest.fixture
def get_user_1():
    response = requests.post(config.url + 'auth/register/v2', data={
        'email': 'owner@test.com', 
        'password': 'spotato', 
        'name_first': 'owner', 
        'name_last' : 'one'
        })
    return response.json()

# Fixture to register someone and returns a dictionary of {token, auth_user_id}
@pytest.fixture
def auth_id_v2(clear_server):
    response = requests.post(config.url + 'auth/register/v2', data={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    return response.json()


# Dont know how to test register without dirctly calling functions or using another endpoint like auth/login/v2.
# So this test is the same test as the one in auth_login_v2

# Do fixtures call from left to right?
# if not then the server may run into the case where it runs get_user1 and then clears or it runs get_user1 and sometimes gets an input error
def test_standard(clear_server, get_user_1):
    response = requests.post(config.url + 'auth/login/v2', data={'email': 'owner@test.com', 'password': 'spotato'}).json()

    assert response['auth_user_id'] == get_user_1['auth_user_id'], 'Valid case: Auth_id not consistant across login and register'

def test_invalid_email(clear_server):
    bad_email_response = (requests.post(config.url + 'auth/register/v2', data={
        'email': 'inv$alid@gmail.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })).json()
    assert(bad_email_response.status_code == 400)

    bad_email_response_2 = (requests.post(config.url + 'auth/register/v2', data={
        'email': 'inv$alid@gma(il.com.au', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })).json()
    assert(bad_email_response_2.status_code == 400)
    
    bad_email_response_3 = (requests.post(config.url + 'auth/register/v2', data={
        'email': 'in/v$alid@gm@il.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })).json()
    assert(bad_email_response_3.status_code == 400)

# A test that expects a InputError when the email given already exists.
def test_duplicate_email(auth_id_v2):
    response = (requests.post(config.url + 'auth/register/v2', data={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })).json()
    assert(response.status_code == 400)

def test_invalid_password_v2(clear_server):
    bad_password = (requests.post(config.url + 'auth/register/v2', data={
        'email': 'example@email.com', 
        'password': 'n', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })).json()
    assert(bad_password.status_code == 400)

def test_invalid_first_name_v2(clear_server):
    short_first_name = (requests.post(config.url + 'auth/register/v2', data={
        'email': 'example@email.com', 
        'password': 'password', 
        'name_first': '', 
        'name_last' : 'smith'
        })).json()
    assert(short_first_name.status_code == 400)

    too_long = "password" * 50

    long_first_name = (requests.post(config.url + 'auth/register/v2', data={
        'email': 'example@email.com', 
        'password': 'password', 
        'name_first': too_long, 
        'name_last' : 'smith'
        })).json()
    assert(long_first_name.status_code == 400)

def test_invalid_last_name_v2(clear_server):
    short_last_name = (requests.post(config.url + 'auth/register/v2', data={
        'email': 'example@email.com', 
        'password': 'password', 
        'name_first': 'johhnn', 
        'name_last' : ''
        })).json()
    assert(short_last_name.status_code == 400)

    too_long = "password" * 50

    long_last_name = (requests.post(config.url + 'auth/register/v2', data={
        'email': 'example@email.com', 
        'password': 'password', 
        'name_first': 'johhhnnn', 
        'name_last' : too_long
        })).json()
    assert(long_last_name.status_code == 400)

# Token generation is not known yet.
# Will implement token related tests later. 
def test_invalid_register_return_token_v2():
    return



# A test that checks if handle genneration has been correctly generated. 
def test_appended_handle_number(clear_server, get_user_1):
    user_1_dict = requests.get(config.url + 'user/profile/v1', params={'token': get_user_1['token'], 'u_id': get_user_1['auth_user_id']}).json()
    assert(user_1_dict['handle'] == "ownerone")

    response = requests.post(config.url + 'auth/register/v2', data={
        'email': 'owner1@test.com', 
        'password': 'spotato', 
        'name_first': 'owner', 
        'name_last' : 'one'
        })
    user_2 = response.json()
    user_2_dict = requests.get(config.url + 'user/profile/v1', params={'token': user_2['token'], 'u_id': user_2['auth_user_id']}).json()

    assert(user_2_dict['handle'] == "ownerone0"), 'handle generation of appended handle number'

def test_concatenated_length(clear, extract_handle):
    auth_user_id = auth_register_v1("example@email.com", "password", "johnsmithjohnsmithjohnsmithjohnsmithssmsmsmsmsms", "smith")
    channel_id = channels_create_v1(auth_user_id['auth_user_id'], 'test_channel', True)
    handle = extract_handle(channel_details_v1(auth_user_id['auth_user_id'], channel_id['channel_id']))
    assert len(handle) <= 20

