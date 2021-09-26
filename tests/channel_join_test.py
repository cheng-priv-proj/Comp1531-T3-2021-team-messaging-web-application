import pytest

from src.channel import channel_join_v1

from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channels import channels_listall_v1

from src.other import clear_v1
from src.error import InputError
from src.error import AccessError

## Was thinking of maybe reworking the way the fixture is run (Maybe return list?) Not sure if its better or worse though.
## Start from 1 or 0? I'm assuming 1 since length but.

@pytest.fixture
def clear():
    clear_v1()

# Automatically create owner user id and channel id. Both are 1 by default.
@pytest.fixture
def register():
    owner_id = auth_register_v1('owner@test.com', 'password', 'owner', 'one')
    channel_id = channels_create_v1(owner_id['auth_user_id'], 'test channel', True)
    return {**owner_id, **channel_id}
    
def test_valid_id(clear, register):
    auth_user_id = auth_register_v1('member@test.com', 'password', 'member', 'one')
    channel_id = register['channel_id']
    channel_join_v1(auth_user_id, channel_id)
    assert channels_listall_v1(auth_user_id) == [
        {
            'channel_id': channel_id, 
            'name': 'test channel'
        }
    ]

def test_multiple_servers(clear, register):
    # Creates second owner and server
    owner2_auth_user_id = auth_register_v1('owner2@test.com', 'password', 'owner', 'two')
    channel2_id = channels_create_v1(owner2_auth_user_id, 'test channel2', True)
    # Creates a new user and sets channel_id of fixture channel to be 0
    auth_user_id = auth_register_v1('member@test.com', 'password', 'member', 'one')
    channel1_id = register['channel_id']
    channel_join_v1(auth_user_id, channel1_id)
    channel_join_v1(auth_user_id, channel2_id)
    assert channels_listall_v1(auth_user_id) == [
        {
            'channel_id': channel1_id, 
            'name': 'test channel'
        },
        {
            'channel_id': channel2_id, 
            'name': 'test channel2'
        }
    ]

def test_invalid_channel_id(clear, register):
    auth_user_id = auth_register_v1('member@test.com', 'password', 'member', 'one')
    invalid_channel_id = 100
    with pytest.raises(InputError):
        channel_join_v1(auth_user_id, invalid_channel_id)

def test_invalid_user_id(clear, register):
    invalid_auth_user_id = 100
    channel_id = register['channel_id']
    with pytest.raises(InputError):
        channel_join_v1(invalid_auth_user_id, channel_id)

def test_already_member(clear, register):
    auth_user_id = auth_register_v1('member@test.com', 'password', 'member', 'one')
    channel_id = register['channel_id']
    channel_join_v1(auth_user_id, channel_id)
    with pytest.raises(InputError):
        channel_join_v1(auth_user_id, channel_id)

def test_already_owner(clear, register):
    owner_auth_user_id = register['auth_user_id']
    channel_id = register['channel_id']
    with pytest.raises(InputError):
        channel_join_v1(owner_auth_user_id, channel_id)

def test_private_not_owner(clear):
    # Register owner and private channel
    owner_auth_user_id = auth_register_v1('owner@test.com', 'password', 'owner', 'one')
    channel_id = channels_create_v1(owner_auth_user_id, 'test channel', False)
    # Create member
    auth_user_id = auth_register_v1('member@test.com', 'password', 'member', 'one')
    with pytest.raises(AccessError):
        channel_join_v1(auth_user_id, channel_id)