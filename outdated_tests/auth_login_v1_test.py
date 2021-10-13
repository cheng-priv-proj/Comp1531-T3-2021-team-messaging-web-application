import pytest

from src.auth import *
from src.error import InputError
from src.other import clear_v1

# Fixture to reset data store before every test
@pytest.fixture
def clear():
    clear_v1()

# Extracts the auth_user_id from a given dictionary.
@pytest.fixture
def extract_user():
    def extract_user_id_function(auth_user_id_dict):
        return auth_user_id_dict['auth_user_id']
    return extract_user_id_function

# Fixture that registers a valid user.
@pytest.fixture
def auth_id(clear):
    return auth_register_v1("example@email.com", "potato", "john", "smith")
    
def test_standard(clear, auth_id, extract_user):
    auth_login_id = extract_user(auth_login_v1("example@email.com", "potato"))
    assert isinstance(auth_login_id, int)
    assert auth_login_id == extract_user(auth_id)

def test_incorrect_password(clear, auth_id):
    with pytest.raises(InputError):
        auth_login_v1("example@email.com", "notpotato")

# Test that expects an input error when given a non-existant email.
def test_email_does_not_exist(clear, auth_id):
    with pytest.raises(InputError):
        auth_login_v1("invalid@gmail.com", "password")

    with pytest.raises(InputError):
        auth_login_v1("inv$alid@gmail.com", "password")

# Test that expects an input error when all the fields are invalid. 
def test_all_incorrect(clear, auth_id):
    with pytest.raises(InputError):
        auth_login_v1("invalid@gmail.com", "notpotato")