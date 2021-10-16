import pytest

from src.channel import channel_join_v1

from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channels import channels_list_v1

from src.other import clear_v1
from src.error import InputError
from src.error import AccessError

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

def test_valid_id(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(auth_register_v1('member@test.com', 'password', 'member', 'one'))
    channel_id = extract_channel(register)

    channel_join_v1(auth_user_id, channel_id)

    assert channels_list_v1(auth_user_id) == {
        'channels': [
        	{
                'channel_id': channel_id, 
                'name': 'test channel'
            }
        ],
    }

def test_multiple_servers(clear, register, extract_user, extract_channel):
    channel1_id = extract_channel(register)
    owner2_auth_user_id = extract_user(auth_register_v1('owner2@test.com', 'password', 'owner', 'two'))
    channel2_id = extract_channel(channels_create_v1(owner2_auth_user_id, 'test channel2', True))

    auth_user_id = extract_user(auth_register_v1('member@test.com', 'password', 'member', 'one'))
    
    channel_join_v1(auth_user_id, channel1_id)
    channel_join_v1(auth_user_id, channel2_id)

    assert channels_list_v1(auth_user_id) == {
        'channels': [
        	{
                'channel_id': channel1_id, 
                'name': 'test channel'
            },
            {
                'channel_id': channel2_id, 
                'name': 'test channel2'
            }
        ],
    }

def test_invalid_channel_id(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(auth_register_v1('member@test.com', 'password', 'member', 'one'))
    invalid_channel_id = 100

    with pytest.raises(InputError):
        channel_join_v1(auth_user_id, invalid_channel_id)

def test_invalid_user_id(clear, register, extract_user, extract_channel):
    invalid_auth_user_id = 100
    channel_id = extract_channel(register)

    with pytest.raises(AccessError):
        channel_join_v1(invalid_auth_user_id, channel_id)

# Test expecting prority to AccessError when an invalid auth_id and channel_id are given.
def test_invalid_user_id_and_invalid_channel_id(clear, register, extract_user, extract_channel):
    invalid_auth_user_id = 100
    invalid_channel_id = 100

    with pytest.raises(AccessError):
        channel_join_v1(invalid_auth_user_id, invalid_channel_id)

def test_already_member(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(auth_register_v1('member@test.com', 'password', 'member', 'one'))
    channel_id = extract_channel(register)

    channel_join_v1(auth_user_id, channel_id)

    with pytest.raises(InputError):
        channel_join_v1(auth_user_id, channel_id)

def test_already_owner(clear, register, extract_user, extract_channel):
    owner_auth_user_id = extract_user(register)
    channel_id = extract_user(register)

    with pytest.raises(InputError):
        channel_join_v1(owner_auth_user_id, channel_id)

def test_private_not_owner(clear, extract_user, extract_channel):
    owner_auth_user_id = extract_user(auth_register_v1('owner@test.com', 'password', 'owner', 'one'))
    channel_id = extract_channel(channels_create_v1(owner_auth_user_id, 'test channel', False))
    
    auth_user_id = extract_user(auth_register_v1('member@test.com', 'password', 'member', 'one'))

    with pytest.raises(AccessError):
        channel_join_v1(auth_user_id, channel_id)

# Testing that global owner has the correct permissions.
def test_global_owner(clear, extract_user, extract_channel):
    owner_auth_user_id = extract_user(auth_register_v1('owner@test.com', 'password', 'owner', 'one'))
    auth_id_1 = extract_user(auth_register_v1('user1@test.com', 'password1', 'userasd', 'oneee'))
    auth_id_2 = extract_user(auth_register_v1('user2@test.com', 'password2', 'userrr', 'twooo'))

    channel_id = extract_channel(channels_create_v1(auth_id_1, 'testing_channel3', False))
    channel_join_v1(owner_auth_user_id, channel_id)

    channel_list = channels_list_v1(owner_auth_user_id)

    assert channel_list == { 
        'channels': [
            {
                'channel_id': channel_id, 
                'name': 'testing_channel3'
            }
        ]
    }

    with pytest.raises(AccessError):
        channel_join_v1(auth_id_2, channel_id)

