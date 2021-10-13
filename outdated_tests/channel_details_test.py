import pytest
from src.channels import channels_create_v1
from src.other import clear_v1
from src.channel import channel_details_v1
from src.auth import auth_register_v1

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

# Test expecting AccessError when given a valid Auth_id that is not in the channel.
def test_user_with_no_access_to_channel(clear, register, extract_channel, extract_user):
    auth_user_id_invalid = extract_user(auth_register_v1("invalid@email.com", "12345678", "testname", "testlname"))
    channel_1 = extract_channel(register)

    with pytest.raises(AccessError):
        channel_details_v1(auth_user_id_invalid, channel_1)

def test__invalid_types(clear, register, extract_channel, extract_user):
    with pytest.raises(TypeError):
        channel_details_v1({}, {})

def test_invalid_channel_id(clear, register, extract_user):
    auth_user_id = extract_user(register)

    with pytest.raises(InputError):
        channel_details_v1(auth_user_id, 10000)

def test_invalid_auth_id(clear, register, extract_channel):
    channel_id = extract_channel(register)

    with pytest.raises(AccessError):
        channel_details_v1(10000, channel_id)

def test_returns_all_info(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_1 = extract_channel(register)

    details = channel_details_v1(auth_user_id, channel_1)
    assert details["name"] == 'test channel'
    assert details["is_public"] == True
    assert details.get("owner_members") == [
        {
            'u_id': auth_user_id,
            'email': 'owner@test.com',
            'name_first': 'owner',
            'name_last': 'one',
            'handle_str': 'ownerone'
        }
    ]
    assert details["all_members"] == [
        {
            'u_id': auth_user_id,
            'email': 'owner@test.com',
            'name_first': 'owner',
            'name_last': 'one',
            'handle_str': 'ownerone'
        }
    ]

