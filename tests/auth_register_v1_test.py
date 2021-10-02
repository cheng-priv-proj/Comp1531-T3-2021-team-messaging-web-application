import pytest

import sys

from src.auth import *
from src.error import InputError
from src.other import clear_v1
from src.channel import channel_details_v1
from src.channels import channels_create_v1

@pytest.fixture
def clear():
    clear_v1()

def test_standard(clear):
    
    output = auth_register_v1("example@email.com", "password", "john", "smith")
    assert isinstance(output["auth_user_id"], int)
    login = auth_login_v1("example@email.com", "password")
    assert output["auth_user_id"] == login["auth_user_id"]

    output = auth_register_v1("Example@EmaiL.orG.au", "pAssW0rd", "John", "Smith")
    assert isinstance(output["auth_user_id"], int)
    login = auth_login_v1("Example@EmaiL.orG.au", "pAssW0rd")
    assert output["auth_user_id"] == login["auth_user_id"]
    
    output = auth_register_v1("emailPerson@mailchimp.potato", "9d-P<vBy9qmk/4C", "john", "smith")
    assert isinstance(output["auth_user_id"], int)
    login = auth_login_v1("emailPerson@mailchimp.potato", "9d-P<vBy9qmk/4C")
    assert output["auth_user_id"] == login["auth_user_id"]

def test_invalid_email(clear):
    with pytest.raises(InputError):
        auth_register_v1("inv$alid@gmail.com", "password", "john", "smith")
    
    with pytest.raises(InputError):
        auth_register_v1("inv$alid@gma(il.com.au", "password", "john", "smith")

    with pytest.raises(InputError):
        auth_register_v1("in/v$alid@gm@il.com", "password", "john", "smith")


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

    word = "password"
    too_long = word * 50

    with pytest.raises(InputError):
        auth_register_v1("example@email.com", "no", too_long, "smith")

def test_invalid_last_name(clear):
    with pytest.raises(InputError):
        auth_register_v1("example@email.com", "password", "john", "")

    word = "password"
    too_long = word * 50

    with pytest.raises(InputError):
        auth_register_v1("example@email.com", "no", "john", too_long)

def test_appended_handle_number(clear):
    output1 = auth_register_v1("example@email.com", "password", "john", "smith")
    output2 = auth_register_v1("example2@email.com", "password", "john", "smith")

    channel_id = channels_create_v1(output2['auth_user_id'], 'test_channel', True)
    channel_details = channel_details_v1(output2['auth_user_id'], channel_id['channel_id'])
    assert channel_details['owner_members'][0]['handle_str'] == 'johnsmith0'

    output3 = auth_register_v1("example3@email.com", "password", "john", "smith")
    channel_id2 = channels_create_v1(output3['auth_user_id'], 'test_channel', True)
    channel_details2 = channel_details_v1(output3['auth_user_id'], channel_id2['channel_id'])
    assert channel_details2['owner_members'][0]['handle_str'] == 'johnsmith1'

    output4 = auth_register_v1("example4@email.com", "password", "john", "smith")
    channel_id3 = channels_create_v1(output4['auth_user_id'], 'test_channel', True)
    channel_details3 = channel_details_v1(output4['auth_user_id'], channel_id3['channel_id'])
    assert channel_details3['owner_members'][0]['handle_str'] == 'johnsmith2'

def test_concatenated_length(clear):
    auth_user_id = auth_register_v1("example@email.com", "password", "johnsmithjohnsmithjohnsmithjohnsmithssmsmsmsmsms", "smith")
    channel_id = channels_create_v1(auth_user_id['auth_user_id'], 'test_channel', True)
    channel_details = channel_details_v1(auth_user_id['auth_user_id'], channel_id['channel_id'])
    assert len(channel_details['owner_members'][0]['handle_str']) <= 20