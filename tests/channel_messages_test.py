import pytest

from src.auth import auth_register_v1

from src.channel import channel_messages_v1

from src.channels import channels_create_v1

from src.other import clear_v1

from src.error import InputError
from src.error import AccessError

# Registers a user who is the owner of a created channel. 
@pytest.fixture
def clear_and_register():
    clear_v1()
    auth_user_id = auth_register_v1('test@gmail.com', '124562343', 'first', 'last').get('auth_user_id')
    channel_id = channels_create_v1(auth_user_id, 'test channel', True).get('channel_id')
    return (auth_user_id, channel_id)

def test_empty_messages(clear_and_register):  
    auth_user_id = clear_and_register[0]
    channel_id = clear_and_register[1]
    assert {'messages': [], 'start': 0, 'end': -1} == channel_messages_v1(auth_user_id, channel_id, 0)

def test_valid_channel_id_and_unauthorized_auth_user_id(clear_and_register):
    channel_id = clear_and_register[1]
    invalid_auth_user_id = auth_register_v1('test2@gmail.com', '12234234323', 'first', 'last').get('auth_user_id')
    with pytest.raises(AccessError):
        channel_messages_v1(invalid_auth_user_id, channel_id, 0)

def test_invalid_channel_id(clear_and_register):
    auth_user_id = clear_and_register[0]
    channel_id = clear_and_register[1]
    with pytest.raises(InputError):
        channel_messages_v1(auth_user_id, 123123123123, 0)

# Test expecting InputError when given a negative starting index.
def test_negative_start(clear_and_register):
    auth_user_id = clear_and_register[0]
    channel_id = clear_and_register[1]
    with pytest.raises(InputError):
        channel_messages_v1(auth_user_id, channel_id, -30)

def test_start_greater_than_messages(clear_and_register):
    auth_user_id = clear_and_register[0]
    channel_id = clear_and_register[1]
    with pytest.raises(InputError):
        channel_messages_v1(auth_user_id, channel_id, 10000)

# Test that expects AccessError priority when both message index and auth id are invalid.
def test_start_greater_than_messages_and_invalid_auth_id(clear_and_register):
    invalid_auth_user_id = 100
    channel_id = clear_and_register[1]
    with pytest.raises(AccessError):
        channel_messages_v1(invalid_auth_user_id, channel_id, 10000)

# Test that expects AccessError priority when both channel and auth id are invalid.
def test_invalid_channel_id_and_unauthorized_user(clear_and_register):
    with pytest.raises(AccessError):
        channel_messages_v1(123123123, 12312312345, 0)

def test_invalid_auth_user_id(clear_and_register):
    channel_id = clear_and_register[1]
    with pytest.raises(AccessError):
        channel_messages_v1(21312123, channel_id, 0)

def test_invalid_types_v1(clear_and_register):
    with pytest.raises(TypeError):
        channel_messages_v1('string', 'string', 'string')

def test_invalid_types_v2(clear_and_register):
    with pytest.raises(TypeError):
        channel_messages_v1([], [], [])