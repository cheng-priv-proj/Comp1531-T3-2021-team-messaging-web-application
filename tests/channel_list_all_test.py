import pytest

from src.auth import auth_register_v1

from src.channels import channels_listall_v1
from src.channels import channels_create_v1

from src.error import AccessError
from src.other import clear_v1

@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def get_user1():
    auth_user_id_dict = auth_register_v1('validemail100@gmail.com', 'validpassword', 'Randomname', 'Randomsurname')
    return auth_user_id_dict['auth_user_id']

@pytest.fixture
def get_user2():
    auth_user_id_dict = auth_register_v1('validemail200@gmail.com', 'Validpassword', 'Randomnamee', 'Randomsurnamee')
    return auth_user_id_dict['auth_user_id']

@pytest.fixture
def get_user3():
    auth_user_id_dict = auth_register_v1('validemail300@gmail.com', 'Validpassworddd', 'Randomnameee', 'Randomsurnameee')
    return auth_user_id_dict['auth_user_id']

@pytest.fixture
def extract_channel():
    def extract_channel_id_function(channel_id_dict):
        return channel_id_dict['channel_id']
    return extract_channel_id_function

# Testing the standard valid case.
def test_channel_list_all_valid(clear, get_user1, extract_channel):
    
    channel_id1 = extract_channel(channels_create_v1(get_user1, 'testing_channel', True))
    channel_list = (channels_listall_v1(get_user1))

    assert(channel_list == { 'channels': [{'channel_id': channel_id1, 'name': 'testing_channel'}]}), "channel_list_all: Failed standard valid case (one channel)"

    channel_id2 = extract_channel(channels_create_v1(get_user1, 'testing_channel_2', True))
    channel_list = (channels_listall_v1(get_user1))
    
    assert(channel_list == { 'channels': [{'channel_id': channel_id1, 'name': 'testing_channel'}, {'channel_id': channel_id2, 'name': 'testing_channel_2'}]}), "channel_list_all: Failed standard valid case (two channels)"

# Testing the case where there are no channels 
def test_channel_list_all_nochannels(clear, get_user1):

    channel_list_all = (channels_listall_v1(get_user1))
    assert(channel_list_all == { 'channels': []}), "channel_list_all: list of channels is not empty with no channels created"

# Testing that the function returns all channels regardless whether or not the auth id is part of them
def test_channel_list_all_other_owners(clear, get_user1, get_user2, extract_channel):

    channel_id1 = extract_channel(channels_create_v1(get_user1, 'testing_channel3', True))
    channel_id2 = extract_channel(channels_create_v1(get_user2, 'testing_channel4', True))

    channel_list = (channels_listall_v1(get_user1))
    channel_list2 = (channels_listall_v1(get_user2))

    assert(channel_list == { 'channels': [{'channel_id': channel_id1, 'name': 'testing_channel3'}, {'channel_id': channel_id2, 'name': 'testing_channel4'}]}), "channel_list_all: Failed to return all channels that exist"

    assert(channel_list2 == { 'channels': [{'channel_id': channel_id1, 'name': 'testing_channel3'}, {'channel_id': channel_id2, 'name': 'testing_channel4'}]}), "channel_list_all: Failed to return all channels that exist"
    
# Testing that whether a channel is public or private has no effect on the returning list
def test_channel_list_all_public_private(clear, get_user1, get_user2, get_user3,extract_channel):
    channel_id1 = extract_channel(channels_create_v1(get_user1, 'testing_channel3', False))
    channel_id2 = extract_channel(channels_create_v1(get_user2, 'testing_channel4', True))
    channel_id3 = extract_channel(channels_create_v1(get_user3, 'testing_channel5', False))

    channel_list = (channels_listall_v1(get_user1))
    channel_list2 = (channels_listall_v1(get_user2))
    channel_list3 = channels_listall_v1(get_user3)

    assert(channel_list == { 'channels': [{'channel_id': channel_id1, 'name': 'testing_channel3'}, {'channel_id': channel_id2, 'name': 'testing_channel4'}, {'channel_id': channel_id3, 'name': 'testing_channel5'}]}), "channel_list_all: Failed to return all channels that exist"
    assert(channel_list2 == { 'channels': [{'channel_id': channel_id1, 'name': 'testing_channel3'}, {'channel_id': channel_id2, 'name': 'testing_channel4'}, {'channel_id': channel_id3, 'name': 'testing_channel5'}]}), "channel_list_all: Failed to return all channels that exist"
    assert(channel_list3 == { 'channels': [{'channel_id': channel_id1, 'name': 'testing_channel3'}, {'channel_id': channel_id2, 'name': 'testing_channel4'}, {'channel_id': channel_id3, 'name': 'testing_channel5'}]}), "channel_list_all: Failed to return all channels that exist"

def test_invalid_auth_id(clear):
    invalid_auth_user_id = 1000
    with pytest.raises(AccessError):
        channels_listall_v1(invalid_auth_user_id)