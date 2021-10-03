import pytest

from src.auth import *
from src.error import InputError
from src.other import clear_v1

# Fixture to reset data store before every test
@pytest.fixture
def clear():
    clear_v1()

# Fixture that registers a valid user.
@pytest.fixture
def auth_id(clear):
    return auth_register_v1("example@email.com", "potato", "john", "smith")
    
def test_standard(clear, auth_id):
    output = auth_login_v1("example@email.com", "potato")
    assert isinstance(output["auth_user_id"], int)
    assert output["auth_user_id"] == auth_id['auth_user_id']

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