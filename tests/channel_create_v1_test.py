import pytest
from src.channels import channels_create_v1
from src.other import clear_v1
from src.channel import channel_details_v1
from src.auth import auth_register_v1

from src.error import AccessError, InputError


# Returns only the value and not the dict
@pytest.fixture
def extract_user():
    def extract_user_id_function(auth_user_id_dict):
        return auth_user_id_dict['auth_user_id']
    return extract_user_id_function

# Returns only the value and not the dict
@pytest.fixture
def extract_channel():
    def extract_channel_id_function(channel_id_dict):
        return channel_id_dict['channel_id']
    return extract_channel_id_function

@pytest.fixture
def clear():
    clear_v1()

# Automatically create owner user id and channel id. Both are 1 by default.
@pytest.fixture
def register():
    owner_id_dict = auth_register_v1('owner@test.com', 'password', 'owner', 'one')
    owner_user_id = owner_id_dict['auth_user_id']
    channel_id_dict = channels_create_v1(owner_user_id, 'test channel', True)
    return {**owner_id_dict, **channel_id_dict}

# parameters: auth_user_id (int), name (string), is_public (boolean)
# return type: channel_id (int)

def test_channel_id_type(register, extract_channel, extract_user):
    auth_user_id = extract_user(register)
    channel_dict = channels_create_v1(auth_user_id, 'test', True)
    assert isinstance(channel_dict, dict) == True

    
def test_public_channel(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_1 = extract_channel(register)
    
    #look in database and check if channel with that id is public
    details = channel_details_v1(auth_user_id, channel_1)
    print(details)
    assert details["is_public"] == True
    

def test_private_channel(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_id = extract_channel(channels_create_v1(auth_user_id, "name", False))
    
    #look in database and check if channel with that id is public
    details = channel_details_v1(auth_user_id, channel_id)
    assert details["is_public"] == False

def test_invalid_user_id(clear):
    auth_user_id = 100000
    
    with pytest.raises(AccessError):
        channels_create_v1(auth_user_id, "name", False)

def test_unique_channel_id(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_1 = extract_channel(register)
    channel_2 = extract_channel(channels_create_v1(auth_user_id, "name2", False))

    assert channel_1 != channel_2


def test_creator_joins_channel(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_1 = extract_channel(register)
    
    #look in database and check if channel with that id is public
    details = channel_details_v1(auth_user_id, channel_1)
    assert details["all_members"][auth_user_id]["email"] == "owner@test.com"


def test_becomes_owner(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_1 = extract_channel(register)
    
    #look in database and check if channel with that id is public
    details = channel_details_v1(auth_user_id, channel_1)
    assert details["owner_members"][auth_user_id]["email"] == "owner@test.com"


def test_short_channel_name(clear, register, extract_user):
    auth_user_id = extract_user(register)
    
    with pytest.raises(InputError):
        channels_create_v1(auth_user_id, "", False)


def test_long_channel_name(clear, register, extract_user):
    auth_user_id = extract_user(register)
    
    with pytest.raises(InputError):
        channels_create_v1(auth_user_id, "reallylongname1234567eallylongname1234567", False)





