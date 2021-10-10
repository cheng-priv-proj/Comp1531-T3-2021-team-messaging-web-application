import pytest
import requests
import json
import flask
from src import config

import pytest

from src.auth import *
from src.error import InputError
from src.other import clear_v2
from src.other import clear_v1

# clear_v2, auth_register_v2


# Fixture to reset data store before every test
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
    return auth_register_v2("example@email.com", "potato", "john", "smith")



def test_standard_v2(clear, auth_id_v2, extract_user_v2, extract_user_v2_token):
    user_dict = auth_login_v2("example@email.com", "potato")
    auth_login_id = extract_user_v2(user_dict)
    token = extract_user_v2_token(user_dict)
    assert auth_login_id == 
    
    
    assert isinstance(auth_login_id, int)
    assert auth_login_id == au

def test_incorrect_password_v2(clear, auth_id):
    with pytest.raises(InputError):
        auth_login_v1("example@email.com", "notpotato")

# Test that expects an input error when given a non-existant email.
def test_email_does_not_exist_v2(clear, auth_id):
    with pytest.raises(InputError):
        auth_login_v1("invalid@gmail.com", "password")

    with pytest.raises(InputError):
        auth_login_v1("inv$alid@gmail.com", "password")

# Test that expects an input error when all the fields are invalid. 
def test_all_incorrect_v2(clear, auth_id):
    with pytest.raises(InputError):
        auth_login_v1("invalid@gmail.com", "notpotato")

def test_invalid_return_token_v2():
    return