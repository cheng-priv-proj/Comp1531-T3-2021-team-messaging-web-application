import pytest

from src.auth import auth_login_v1
from src.auth import auth_register_v1

from src.channels import channels_list_v1
from src.channels import channels_listall_v1
from src.channels import channels_create_v1

from src.channel import channel_join_v1

from src.error import AccessError
from src.other import clear_v1

#### ASSUMES THAT ALL AUTH ID GIVEN IS A VALID AUTH ID ####
#### NEED TO IMPLEMENT ADDIDTIONAL TESTS OR ADD ASSUPTIONS TO COVER THIS SCENARIO ##

@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def get_user1():
    #def extract_user_id_function():
    auth_user_id_dict = auth_register_v1('validemail100@gmail.com', 'validpassword', 'Randomname', 'Randomsurname')
    return auth_user_id_dict['auth_user_id']
    #return extract_user_id_function

@pytest.fixture
def get_user2():
    auth_user_id_dict = auth_register_v1('validemail200@gmail.com', 'Validpassword', 'Randomnamee', 'Randomsurnamee')
    return auth_user_id_dict['auth_user_id']

@pytest.fixture
def extract_channel():
    def extract_channel_id_function(channel_id_dict):
        return channel_id_dict['channel_id']
    return extract_channel_id_function

# Standard test for a valid input/output. Tests for single and multi channel
def test_channel_list_valid(clear, get_user1, extract_channel):
    channel_id1 = extract_channel(channels_create_v1(get_user1, 'testing_channel', True))
    channel_list = (channels_list_v1(get_user1))

    assert(channel_list == { 'channels': [{'channel_id': channel_id1, 'name': 'testing_channel'}]}), "Failed channel_list standard valid case (one channel)"

    channel_id2 = extract_channel(channels_create_v1(get_user1, 'testing_channel_2', True))
    channel_list = (channels_list_v1(get_user1))

    # <<<<<NEED TO CLARIFY WHAT TYPE CHANNEL LIST IS>>>>>
    # ENSURE THAT IT IS A LIST OF DICTIONARIES
    # IF testing error occurs, check this first.
    assert(channel_list == { 'channels': [{'channel_id': channel_id1, 'name': 'testing_channel'}, {'channel_id': channel_id2, 'name': 'testing_channel_2'}]}), "Failed channel_list standard valid case (two channels)"

# testing for an empty list of channels
def test_channel_list_nochannels(clear, get_user1):
    channel_list = (channels_list_v1(get_user1))
    assert(channel_list == { 'channels': []}), "channel_list: list of channels is not empty with no channels created"



'''
# tests output when given an invalid auth id input
def test_channel_list_unknown_auth_test():
    clear_v1()
    channel_list = (channels_list_v1(420420))
    assert(channel_list == { 'channels': [{}]}), "channel_list: list of channels is not empty when unknown auth id requests channel_list"
'''



# Testing if the function returns any channels the user is not part of
def test_channel_list_other_owners_test(clear, get_user1, get_user2, extract_channel):
    channel_id1 = extract_channel(channels_create_v1(get_user1, 'testing_channel3', True))
    channel_id2 = extract_channel(channels_create_v1(get_user2, 'testing_channel4', True))
    channel_list = (channels_list_v1(get_user1))
    channel_list2 = (channels_list_v1(get_user2))

    assert(channel_list == { 'channels': [{'channel_id': channel_id1, 'name': 'testing_channel3'}]}), "channel_list: Failed to return channels only owner is part of"

    assert(channel_list2 == { 'channels': [{'channel_id': channel_id2, 'name': 'testing_channel4'}]}), "channel_list: Failed to return channels only owner is part of"
    
# tests the case that a user joins a new channel, and looking for an update the the list
def test_channel_list_after_newjoin_test(clear, get_user1, get_user2, extract_channel):
    channel_id1 = extract_channel(channels_create_v1(get_user1, 'testing_channel3', True))
    channel_join_v1(get_user2, channel_id1)
    channel_list = (channels_list_v1(get_user2))
    assert(channel_list == { 'channels': [{'channel_id': channel_id1, 'name': 'testing_channel3'}]}), "channels_list: incorrect channel_list after the user joins a new channel "
    
def test_invalid_auth_id(clear):
    invalid_auth_user_id = 1000
    with pytest.raises(AccessError):
        channels_list_v1(invalid_auth_user_id)
