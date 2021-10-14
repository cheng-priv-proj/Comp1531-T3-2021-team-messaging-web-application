import pytest

from src.auth import auth_register_v1

from src.channels import channels_list_v1
from src.channels import channels_create_v1

from src.channel import channel_join_v1

from src.error import AccessError
from src.other import clear_v1

@pytest.fixture
def clear():
    clear_v1()

# Registers a user and returns numeric auth_id.
@pytest.fixture
def auth_user_id1():
    auth_user_id_dict = auth_register_v1('validemail100@gmail.com', 'validpassword', 'Randomname', 'Randomsurname')
    return auth_user_id_dict['auth_user_id']
    #return extract_user_id_function

@pytest.fixture
def auth_user_id2():
    auth_user_id_dict = auth_register_v1('validemail200@gmail.com', 'Validpassword', 'Randomnamee', 'Randomsurnamee')
    return auth_user_id_dict['auth_user_id']

# Extracts the channel_id from a given dictionary.
@pytest.fixture
def extract_channel():
    def extract_channel_id_function(channel_id_dict):
        return channel_id_dict['channel_id']
    return extract_channel_id_function

# Standard test for a valid input/output.
def test_channel_list_valid(clear, auth_user_id1, extract_channel):
    channel_id1 = extract_channel(channels_create_v1(auth_user_id1, 'testing_channel', True))
    channel_list = channels_list_v1(auth_user_id1)

    assert channel_list == { 
        'channels': [
            {
                'channel_id': channel_id1, 
                'name': 'testing_channel'
            }
        ]
    }

    channel_id2 = extract_channel(channels_create_v1(auth_user_id1, 'testing_channel_2', True))
    channel_list = channels_list_v1(auth_user_id1)

    assert channel_list == { 
        'channels': [
            {
                'channel_id': channel_id1, 
                'name': 'testing_channel'
            }, 
            {
                'channel_id': channel_id2, 
                'name': 'testing_channel_2'
            }
        ]
    }

# Testing for an empty list of channels.
def test_channel_list_nochannels(clear, auth_user_id1):
    channel_list = channels_list_v1(auth_user_id1)
    assert channel_list == { 
        'channels': []
    }

# Testing if the function returns any channels the user is not part of.
def test_channel_list_other_owners_test(clear, auth_user_id1, auth_user_id2, extract_channel):
    channel_id1 = extract_channel(channels_create_v1(auth_user_id1, 'testing_channel3', True))
    channel_id2 = extract_channel(channels_create_v1(auth_user_id2, 'testing_channel4', True))
    channel_list = (channels_list_v1(auth_user_id1))
    channel_list2 = (channels_list_v1(auth_user_id2))

    assert channel_list == { 
        'channels': [
            {
                'channel_id': channel_id1, 
                'name': 'testing_channel3'
            }
        ]
    }

    assert channel_list2 == { 
        'channels': [
            {
                'channel_id': channel_id2, 
                'name': 'testing_channel4'
            }
        ]
    }
    
# Tests the case that a user joins a new channel, and looking for an update the the list.
def test_channel_list_after_newjoin_test(clear, auth_user_id1, auth_user_id2, extract_channel):
    channel_id1 = extract_channel(channels_create_v1(auth_user_id1, 'testing_channel3', True))
    channel_join_v1(auth_user_id2, channel_id1)
    channel_list = channels_list_v1(auth_user_id2)
    assert channel_list == { 
        'channels': [
            {
                'channel_id': channel_id1, 
                'name': 'testing_channel3'
            }
        ]
    }
    
# Tests whether the auth id is invalid.
def test_invalid_auth_id(clear):
    invalid_auth_user_id = 1000
    with pytest.raises(AccessError):
        channels_list_v1(invalid_auth_user_id)
