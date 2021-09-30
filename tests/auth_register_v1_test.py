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

    output = auth_register_v1("Example@EmaiL.orG.au", "pAssW0rd", "John", "Smith")
    assert isinstance(output["auth_user_id"], int)

    # Sus test
    #output = auth_register_v1("Examp1e-of_email.address@EmaiL.C0m", "pas./s_wor-d", "j0hn", "sm1t\h")
    #assert isinstance(output["auth_user_id"], int)
    
    output = auth_register_v1("emailPerson@mailchimp.potato", "9d-P<vBy9qmk/4C", "john", "smith")
    assert isinstance(output["auth_user_id"], int)
    

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

# Additionally test for correct handle generation behaviour.
# Note that this is not black box testing and the following test/s are dependent
# on the datastore implementation

@pytest.mark.skip(reason="no way of currently testing this")
def test_valid_handle(clear):
    output1 = auth_register_v1("example@email.com", "password", "john", "smith")
    output2 = auth_register_v1("example@email.com", "password", "john", "smith")

    channel_id = channels_create_v1(output2['auth_user_id'], 'test_channel', True)
    channel_details = channel_details_v1(output2['auth_user_id'], channel_id['channel_id'])
    assert channel_details['owner_members']['handle_str'] == 'johnsmith0'

#     store_auth_to_u_id = data_store.get_
#     store_user = data_store.get_u_id_dict()

#     assert store[]
