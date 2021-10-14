import pytest

import sys

from src.auth import *
from src.error import InputError
from src.other import clear_v1
from src.channel import channel_details_v1
from src.channels import channels_create_v1

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

# Extracts the channel from a given dictionary.
@pytest.fixture
def extract_channel():
    def extract_channel_id_function(channel_id_dict):
        return channel_id_dict['channel_id']
    return extract_channel_id_function

# Extracts the handle from a given dictionary.
@pytest.fixture
def extract_handle():
    def extract_handle_function(channel_details_dict):
        return channel_details_dict['owner_members'][0]['handle_str']
    return extract_handle_function

def test_standard(clear, extract_user):
    auth_user_id = extract_user(auth_register_v1("example@email.com", "password", "john", "smith"))
    assert isinstance(auth_user_id, int)
    login_user_id = extract_user(auth_login_v1("example@email.com", "password"))
    assert auth_user_id == login_user_id

    auth_user_id = extract_user(auth_register_v1("Example@EmaiL.orG.au", "pAssW0rd", "John", "Smith"))
    assert isinstance(auth_user_id, int)
    login_user_id = extract_user(auth_login_v1("Example@EmaiL.orG.au", "pAssW0rd"))
    assert auth_user_id == login_user_id
    
    auth_user_id = extract_user(auth_register_v1("emailPerson@mailchimp.potato", "9d-P<vBy9qmk/4C", "john", "smith"))
    assert isinstance(auth_user_id, int)
    login_user_id = extract_user(auth_login_v1("emailPerson@mailchimp.potato", "9d-P<vBy9qmk/4C"))
    assert auth_user_id == login_user_id

def test_invalid_email(clear):
    with pytest.raises(InputError):
        auth_register_v1("inv$alid@gmail.com", "password", "john", "smith")
    
    with pytest.raises(InputError):
        auth_register_v1("inv$alid@gma(il.com.au", "password", "john", "smith")

    with pytest.raises(InputError):
        auth_register_v1("in/v$alid@gm@il.com", "password", "john", "smith")

# A test that expects a InputError when the email given already exists.
def test_duplicate_email(clear):
    auth_register_v1("example@email.com", "password", "john", "smith")
    with pytest.raises(InputError):
        auth_register_v1("example@email.com", "password", "john2", "smith")

def test_invalid_password(clear):
    with pytest.raises(InputError):
        auth_register_v1("example@email.com", "no", "john", "smith")

def test_invalid_first_name(clear):
    with pytest.raises(InputError):
        auth_register_v1("example@email.com", "password", "", "smith")

    too_long = "password" * 50

    with pytest.raises(InputError):
        auth_register_v1("example@email.com", "no", too_long, "smith")

def test_invalid_last_name(clear):
    with pytest.raises(InputError):
        auth_register_v1("example@email.com", "password", "john", "")

    word = "password"
    too_long = word * 50

    with pytest.raises(InputError):
        auth_register_v1("example@email.com", "no", "john", too_long)

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