import pytest

from src.channel import channel_details_v1, channel_invite_v1

from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channels import channels_list_v1
from src.channel import channel_join_v1

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

def test_member_invite(clear, register, extract_user, extract_channel):
    member_user_id = extract_user(auth_register_v1('member@test.com', 'password', 'member', 'one'))
    channel_id = extract_channel(register)
    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))
    
    channel_join_v1(member_user_id, channel_id)
    channel_invite_v1(member_user_id, channel_id, friend_auth_id)

    assert channels_list_v1(friend_auth_id) == {
        'channels': [
        	{
                'channel_id': channel_id,
                'name': 'test channel'
            },
        ],
    }

# Testing that owner has correct permissions.
def test_owner_invite(clear, register, extract_user, extract_channel):
    owner_user_id = extract_user(register)
    channel_id = extract_channel(register)

    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))

    channel_invite_v1(owner_user_id, channel_id, friend_auth_id)

    assert channels_list_v1(friend_auth_id) == {
        'channels': [
        	{
                'channel_id': channel_id,
                'name': 'test channel'
            },
        ],
    }

def test_invite_multiple(clear, register, extract_user, extract_channel): 
    owner2_user_id = extract_user(auth_register_v1('owner2@test.com', 'password', 'owner', 'two'))
    channel2_id = extract_channel(channels_create_v1(owner2_user_id, 'test channel2', True))
    owner1_user_id = extract_user(register)
    channel1_id = extract_channel(register)

    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))

    channel_invite_v1(owner1_user_id, channel1_id, friend_auth_id)
    channel_invite_v1(owner2_user_id, channel2_id, friend_auth_id)

    assert channels_list_v1(friend_auth_id) == {
        'channels': [
            {
                'channel_id': channel1_id,
                'name': 'test channel'
            }, 
            {
                'channel_id': channel2_id,
                'name': 'test channel2'
            },
        ],
    }
    
def test_private_invite(clear, extract_user, extract_channel):
    owner_user_id = extract_user(auth_register_v1('owner@test.com', 'password', 'owner', 'one'))
    channel_id = extract_channel(channels_create_v1(owner_user_id, 'test channel', False))

    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))
    

    channel_invite_v1(owner_user_id, channel_id, friend_auth_id)

    assert channels_list_v1(friend_auth_id) == {
        'channels': [
        	{
                'channel_id': channel_id,
                'name': 'test channel'
            },
        ],
    }

def test_invalid_auth_id(clear, register, extract_user, extract_channel):
    invalid_auth_user_id = 100
    channel_id = extract_channel(register)
    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))

    with pytest.raises(AccessError):
        channel_invite_v1(invalid_auth_user_id, channel_id, friend_auth_id)

def test_invalid_uid(clear, register, extract_user, extract_channel):
    owner_user_id = extract_user(register)
    channel_id = extract_channel(register)
    invalid_friend_auth_id = 10000
    
    with pytest.raises(InputError):
        channel_invite_v1(owner_user_id, channel_id, invalid_friend_auth_id)

def test_invalid_auth_id_and_u_id(clear, register, extract_channel):
    invalid_auth_user_id = 100
    channel_id = extract_channel(register)
    invalid_auth_id = 100

    with pytest.raises(AccessError):
        channel_invite_v1(invalid_auth_user_id, channel_id, invalid_auth_id)

def test_invalid_channel_id(clear, register, extract_user):
    owner_user_id = extract_user(register)
    invalid_channel_id = 100
    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))
    
    with pytest.raises(InputError):
        channel_invite_v1(owner_user_id, invalid_channel_id, friend_auth_id)

def test_already_member(clear, register, extract_user, extract_channel):
    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))
    
    owner_user_id = extract_user(register)
    channel_id = extract_channel(register)

    channel_invite_v1(owner_user_id, channel_id, friend_auth_id)
    with pytest.raises(InputError):
        channel_invite_v1(owner_user_id, channel_id, friend_auth_id)

def test_already_owner(clear, register, extract_user, extract_channel):
    owner_user_id = extract_user(register)
    channel_id = extract_channel(register)

    with pytest.raises(InputError):
        channel_invite_v1(owner_user_id, channel_id, owner_user_id)

def test_unauthorised_invite(clear, register, extract_user, extract_channel):
    notmember_user_id = extract_user(auth_register_v1('member@test.com', 'password', 'member', 'one'))
    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))
    
    channel_id = extract_channel(register)

    with pytest.raises(AccessError):
        channel_invite_v1(notmember_user_id, channel_id, friend_auth_id)

# Test that checks channel list to comfirm successful invite.
def test_is_added(clear, register, extract_user, extract_channel):
    owner_user_id = extract_user(register)
    channel_id = extract_channel(register)
    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))

    channel_invite_v1(owner_user_id, channel_id, friend_auth_id)

    assert channels_list_v1(friend_auth_id) == {
        'channels': [
        	{
                'channel_id': channel_id,
                'name': 'test channel'
            },
        ],
    }