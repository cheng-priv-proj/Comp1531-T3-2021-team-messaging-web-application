import pytest
import requests
import json
import flask
from src import config

from src.auth import *
from src.error import InputError
from src.other import clear_v2

from src.auth import *
from src.other import clear_v1
from src.channel import channel_details_v1
from src.channels import channels_create_v1

# Need to implement handle checking

@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def clear_server():
    clear_v2()

# Extracts the auth_user_id from a given dictionary.
@pytest.fixture
def extract_user_v2():
    def extract_user_id_function(auth_user_id_dict):
        return auth_user_id_dict['auth_user_id']
    return extract_user_id_function

@pytest.fixture
def extract_user_v2_token():
    def extract_user_id_token(auth_user_id_dict):
        return auth_user_id_dict['token']
    return extract_user_id_token

# Fixture that registers a valid user.
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
def test_standard(extract_user_v2, auth_id_v2):
    dict_id_token = requests.post(config.url + 'auth/login/v2', data={'email': 'example@email.com', 'password': 'potato'}).json()
    assert extract_user_v2(dict_id_token) == extract_user_v2(auth_id_v2), 'Valid case: Auth_id not consistant across login and register'

def test_invalid_email(clear):
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


''' NOT SURE ABOUT HANDLE GENERATION
# A test that checks if handle genneration has been correctly generated. 
def test_appended_handle_number(clear, extract_user, extract_handle, extract_channel):
    auth_register_v1("example@email.com", "password", "john", "smith")
    auth1_user_id = extract_user(auth_register_v1("example2@email.com", "password", "john", "smith"))

    channel1_id = extract_channel(channels_create_v1(auth1_user_id, 'test_channel', True))
    handle = extract_handle(channel_details_v1(auth1_user_id, channel1_id))
    assert handle == 'johnsmith0'

    auth2_user_id = extract_user(auth_register_v1("example3@email.com", "password", "john", "smith"))
    channel2_id = extract_channel(channels_create_v1(auth2_user_id, 'test_channel', True))
    handle = extract_handle(channel_details_v1(auth2_user_id, channel2_id))
    assert handle == 'johnsmith1'

    auth3_user_id = extract_user(auth_register_v1("example4@email.com", "password", "john", "smith"))
    channel_id3 = extract_channel(channels_create_v1(auth3_user_id, 'test_channel', True))
    handle = extract_handle(channel_details_v1(auth3_user_id, channel_id3))
    assert handle == 'johnsmith2'

def test_concatenated_length(clear, extract_handle):
    auth_user_id = auth_register_v1("example@email.com", "password", "johnsmithjohnsmithjohnsmithjohnsmithssmsmsmsmsms", "smith")
    channel_id = channels_create_v1(auth_user_id['auth_user_id'], 'test_channel', True)
    handle = extract_handle(channel_details_v1(auth_user_id['auth_user_id'], channel_id['channel_id']))
    assert len(handle) <= 20

'''