import pytest

from src.auth import auth_register_v1

from src.channel import channel_messages_v1

from src.channels import channels_create_v1

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

# Registers a user who is the owner of a created channel. 
@pytest.fixture
def register():
    auth_user_id = auth_register_v1('test@gmail.com', '124562343', 'first', 'last')
    channel_id = channels_create_v1(auth_user_id['auth_user_id'], 'test channel', True)
    return {**auth_user_id, **channel_id}

# Registers a user who is the owner of a created channel. 
@pytest.fixture
def clear():
    clear_v1()
    

def test_empty_messages(clear, register, extract_user, extract_channel):  
    auth_user_id = extract_user(register)
    channel_id = extract_channel(register)
    assert channel_messages_v1(auth_user_id, channel_id, 0) == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

def test_valid_channel_id_and_unauthorized_auth_user_id(clear, register, extract_user, extract_channel):
    channel_id = extract_channel(register)
    invalid_auth_user_id = extract_user(auth_register_v1('test2@gmail.com', '12234234323', 'first', 'last'))
    with pytest.raises(AccessError):
        channel_messages_v1(invalid_auth_user_id, channel_id, 0)

def test_invalid_channel_id(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    invalid_channel_id = 123123123123
    with pytest.raises(InputError):
        channel_messages_v1(auth_user_id, invalid_channel_id, 0)

# Test expecting InputError when given a negative starting index.
def test_negative_start(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_id = extract_channel(register)
    with pytest.raises(InputError):
        channel_messages_v1(auth_user_id, channel_id, -30)

def test_start_greater_than_messages(clear, register, extract_user, extract_channel):
    auth_user_id = extract_user(register)
    channel_id = extract_channel(register)
    with pytest.raises(InputError):
        channel_messages_v1(auth_user_id, channel_id, 10000)

# Test that expects AccessError priority when both message index and auth id are invalid.
def test_start_greater_than_messages_and_invalid_auth_id(clear, register, extract_channel):
    invalid_auth_user_id = 100
    channel_id = extract_channel(register)
    with pytest.raises(AccessError):
        channel_messages_v1(invalid_auth_user_id, channel_id, 10000)

# Test that expects AccessError priority when both channel and auth id are invalid.
def test_invalid_channel_id_and_unauthorized_user(clear):
    with pytest.raises(AccessError):
        channel_messages_v1(123123123, 12312312345, 0)

def test_invalid_auth_user_id(clear, register, extract_channel):
    channel_id = extract_channel(register)
    with pytest.raises(AccessError):
        channel_messages_v1(21312123, channel_id, 0)

def test_invalid_types_v1(clear):
    with pytest.raises(TypeError):
        channel_messages_v1('string', 'string', 'string')

def test_invalid_types_v2(clear):
    with pytest.raises(TypeError):
        channel_messages_v1([], [], [])