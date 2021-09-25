import pytest
import ???

from src.error import InputError
from src.error import AccessError

@pytest.fixture
def clear_and_register():
    clear_v1()
    auth_user_id = auth_register_v1('email': 'test@gmail.com', 'password': 123, 'name_first': 'first', 'name_last': 'last')
    channel_id = channel_create_v1(auth_user_id, 'test channel', True)

def test_channel_messages_v1_functionality_empty_messages(clear_and_register):    
    assert {'messages': [], 'start': 0, 'end': -1} == channel_messages_v1('auth_user_id': auth_user_id, 'channel_id': channel_id, 'start': 0)

def test_channel_messages_v1_valid_channel_id_and_unauthorized_auth_user_id(clear_and_register):
    invalid_auth_user_id = auth_register_v1('email': 'test2@gmail.com', 'password': 2123, 'name_first': 'first2', 'name_last': 'last2')
    with pytest.raises(AccessError):
        channel_messages_v1('auth_user_id': invalid_auth_user_id, 'channel_id': channel_id, 'start': 0)

def test_channel_messages_v1_invalid_channel_id(clear_and_register):
    with pytest.raises(InputError):
        channel_messages_v1('auth_user_id': auth_user_id, 12312031, 'start': 0)

def test_channel_messages_v1_negative_start(clear_and_register):
    with pytest.raises(InputError):
        channel_messages_v1('auth_user_id': auth_user_id, 'channel_id': channel_id, 'start': -30)

def test_channel_messages_v1_start_greater_than_messages(clear_and_register):
    with pytest.raises(InputError):
        channel_messages_v1('auth_user_id': auth_user_id, 'channel_id': channel_id, 'start': 100000)

def test_channel_messages_v1_invalid_channel_id_and_unauthorized_user(clear_and_register):
    invalid_auth_user_id = auth_register_v1('email': 'test2@gmail.com', 'password': 2123, 'name_first': 'first2', 'name_last': 'last2')
    with pytest.raises(InputError):
        channel_messages_v1('auth_user_id': auth_user_id, 'channel_id': channel_id, 'start': 0)

def test_channel_messages_v1_invalid_auth_user_id(clear_and_register):
    with pytest.raises(AccessError):
        channel_messages_v1('auth_user_id': 120391231, 'channel_id': channel_id, 'start': 0)

def test_channel_messages_v1_invalid_types_v1(clear_and_register):
    with pytest.raises(InputError):
        channel_messages_v1('auth_user_id': '', 'channel_id': '', 'start': '')

def test_channel_messages_v1_invalid_types_v2(clear_and_register):
    with pytest.raises(InputError):
        channel_messages_v1('auth_user_id': [], 'channel_id': [], 'start': [])