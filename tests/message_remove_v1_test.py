import pytest
import requests
import json
import flask
from requests.models import Response
from src import config

from src.other import clear_v1


@pytest.fixture
def clear_server():
    requests.delete(config.url + "clear/v1")

# Fixture to register someone and returns a dictionary of {token, auth_user_id}
@pytest.fixture
def get_user_1():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'owner@test.com', 
        'password': 'spotato', 
        'name_first': 'owner', 
        'name_last' : 'one'
        })
    return response.json()

# Fixture to register someone and returns a dictionary of {token, auth_user_id}
@pytest.fixture
def auth_id_v2():
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    return response.json()

'''
message/remove/v1
Given a message_id for a message, this message is removed from the channel/DM


DELETE


Parameters:
    { token, message_id}

Return Type:
    {}

InputError when any of:
      
        message_id does not refer to a valid message within a channel/DM that the authorised user has joined
      
AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:
      
        the message was sent by the authorised user making this request
        the authorised user has owner permissions in the channel/DM
'''

# TO GET MORE COVERAGE, MAYBE DO THE SMAE TESTS WITH THE CHANNELS BUT CHANGE IS_PUBLIC TO PRIVATE and vice versa
# same tests but send more than 50 messages.
# test with non owner member
# need to add test multple messages

#tests owner case
def test_normal_case_channel(clear_server, get_user_1):
    channel_dict = requests.post(config.url + 'channels/create/v2', json= {
        'token': get_user_1['token'], 
        'name': 'test channel', 
        'is_public': True
    }).json()

    extracted_channel_id = channel_dict['channel_id']
    message_dict = requests.post(config.url + 'message/send/v1', json = {
        'token': get_user_1['token'],
        'channel_id': extracted_channel_id,
        'message': 'Hello there' }).json()

    message_id = message_dict['message_id']

    requests.delete(config.url + 'message/remove/v1', json = {
        'token' : get_user_1['token'],
        'message_id': message_id
    })
    
    message_dict = requests.get(config.url + 'channel/messages/v2', json = {
        'token': get_user_1['token'],
        'channel_id': extracted_channel_id, 
        'start': 0 }).json()

    assert message_dict == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

def test_normal_case_non_owner(clear_server, get_user_1, auth_id_v2):
    channel_dict = requests.post(config.url + 'channels/create/v2', json= {
        'token': get_user_1['token'], 
        'name': 'test channel', 
        'is_public': True
    }).json()

    extracted_channel_id = channel_dict['channel_id']

    requests.post(config.url + 'channel/join/v2', json = {
        'token': auth_id_v2['token'],
        'channel_id': extracted_channel_id
    })

    message_dict = requests.post(config.url + 'message/send/v1', json = {
        'token': auth_id_v2['token'],
        'channel_id': extracted_channel_id,
        'message': 'Hello there' }).json()

    message_id = message_dict['message_id']

    requests.delete(config.url + 'message/remove/v1', json = {
        'token' : auth_id_v2['token'],
        'message_id': message_id
    })
    
    message_dict = requests.get(config.url + 'channel/messages/v2', json = {
        'token': auth_id_v2['token'],
        'channel_id': extracted_channel_id, 
        'start': 0 }).json()

    assert message_dict == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

# testing owner can edit other peoples messages
def test_owner_perms(clear_server, get_user_1, auth_id_v2):
    channel_dict = requests.post(config.url + 'channels/create/v2', json= {
        'token': get_user_1['token'], 
        'name': 'test channel', 
        'is_public': True
    }).json()

    extracted_channel_id = channel_dict['channel_id']

    requests.post(config.url + 'channel/join/v2', json = {
        'token': auth_id_v2['token'],
        'channel_id': extracted_channel_id
    })

    message_dict = requests.post(config.url + 'message/send/v1', json = {
        'token': auth_id_v2['token'],
        'channel_id': extracted_channel_id,
        'message': 'Hello there' }).json()

    message_id = message_dict['message_id']

    requests.delete(config.url + 'message/remove/v1', json = {
        'token' : get_user_1['token'],
        'message_id': message_id
    })
    
    message_dict = requests.get(config.url + 'channel/messages/v2', json = {
        'token': get_user_1['token'],
        'channel_id': extracted_channel_id, 
        'start': 0 }).json()

    assert message_dict == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

# message_id does not refer to a valid message within a channel/DM that the authorised user has joined
def test_invalid_message_id(clear_server, get_user_1):
    channel_dict = requests.post(config.url + 'channels/create/v2', json= {
        'token': get_user_1['token'], 
        'name': 'test channel', 
        'is_public': True
    }).json()

    extracted_channel_id = channel_dict['channel_id']

    requests.post(config.url + 'message/send/v1', json = {
        'token': get_user_1['token'],
        'channel_id': extracted_channel_id,
        'message': 'Hello there' }).json()

    message_id = 123213123

    assert requests.delete(config.url + 'message/remove/v1', json = {
        'token' : get_user_1['token'],
        'message_id': message_id
    }).status_code == 400



'''
# AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:
      
        the message was sent by the authorised user making this request
        the authorised user has owner permissions in the channel/DM
'''
@pytest.mark.skip
# non owner removing someone elses message
def test_edit_acess_error(clear_server, get_user_1, auth_id_v2):
    channel_dict = requests.post(config.url + 'channels/create/v2', json= {
        'token': get_user_1['token'], 
        'name': 'test channel', 
        'is_public': True
    }).json()

    extracted_channel_id = channel_dict['channel_id']
    message_dict = requests.post(config.url + 'message/send/v1', json = {
        'token': get_user_1['token'],
        'channel_id': extracted_channel_id,
        'message': 'Hello there' }).json()

    message_id = message_dict['message_id']

    requests.post(config.url + 'channel/join/v2', json = {
        'token': auth_id_v2['token'],
        'channel_id': extracted_channel_id
    })

    assert requests.delete(config.url + 'message/remove/v1', json = {
        'token' : auth_id_v2['token'],
        'message_id': message_id,
    }).status_code == 400


# does not test global owner
@pytest.mark.skip('Not yet implemented')
def test_normal_case_dms(clear_server, get_user_1, auth_id_v2):
    dm_id_dict = requests.post(config.url + 'dm/create/v1', json= {
        'token': get_user_1['token'], 
        'u_ids': [auth_id_v2["auth_user_id"]]
    }).json()
    dm_id = dm_id_dict['dm_id']

    message_dict = (requests.post(config.url + 'message/senddm/v1', json = {
        'token': get_user_1['token'],
        'dm_id': dm_id,
        'message': 'Hello there' }).json())    
    message_id = message_dict['message_id']

    requests.delete(config.url + 'message/remove/v1', json = {
        'token' : get_user_1['token'],
        'message_id': message_id
    })

    message_dict = requests.get(config.url + 'dm/messages/v1', json = {
        'token': get_user_1['token'],
        'dm_id': dm_id, 
        'start': 0 }).json()

    assert message_dict == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

@pytest.mark.skip('Not yet implemented')
def test_normal_case_non_owner_dms(clear_server, get_user_1, auth_id_v2):
    dm_id_dict = requests.post(config.url + 'dm/create/v1', json= {
        'token': get_user_1['token'], 
        'u_ids': [auth_id_v2["auth_user_id"]]
    }).json()
    
    dm_id = dm_id_dict['dm_id']
    message_dict = (requests.post(config.url + 'message/senddm/v1', json = {
        'token': auth_id_v2['token'],
        'dm_id': dm_id,
        'message': 'Hello there' }).json())    

    message_id = message_dict['message_id']

    requests.delete(config.url + 'message/remove/v1', json = {
        'token' : auth_id_v2['token'],
        'message_id': message_id
    })

    message_dict = requests.get(config.url + 'dm/messages/v1', json = {
        'token': auth_id_v2['token'],
        'dm_id': dm_id, 
        'start': 0 }).json()

    assert message_dict == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

# testing owner can edit other peoples messages
@pytest.mark.skip('Not yet implemented')
def test_owner_perms_dms(clear_server, get_user_1, auth_id_v2):
    dm_id_dict = requests.post(config.url + 'dm/create/v1', json= {
        'token': get_user_1['token'], 
        'u_ids': [auth_id_v2["auth_user_id"]]
    }).json()

    dm_id = dm_id_dict['dm_id']
    
    message_dict = (requests.post(config.url + 'message/senddm/v1', json = {
        'token': auth_id_v2['token'],
        'dm_id': dm_id,
        'message': 'Hello there' }).json())    

    message_id = message_dict['message_id']

    requests.delete(config.url + 'message/remove/v1', json = {
        'token' : get_user_1['token'],
        'message_id': message_id
    })

    message_dict = requests.get(config.url + 'dm/messages/v1', json = {
        'token': get_user_1['token'],
        'dm_id': dm_id, 
        'start': 0 }).json()

    assert message_dict == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }


# message_id does not refer to a valid message within a channel/DM that the authorised user has joined
@pytest.mark.skip('Not yet implemented')
def test_invalid_message_id_dms(clear_server, get_user_1, auth_id_v2):
    dm_id_dict = requests.post(config.url + 'dm/create/v1', json= {
        'token': get_user_1['token'], 
        'u_ids': [auth_id_v2["auth_user_id"]]
    }).json()

    dm_id = dm_id_dict['dm_id']
    
    requests.post(config.url + 'message/senddm/v1', json = {
        'token': get_user_1['token'],
        'dm_id': dm_id,
        'message': 'Hello there' }).json()

    message_id = 123213123

    assert requests.delete(config.url + 'message/remove/v1', json = {
        'token' : get_user_1['token'],
        'message_id': message_id
    }).status_code == 400

'''
# AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:
      
        the message was sent by the authorised user making this request
        the authorised user has owner permissions in the channel/DM
'''
# non owner tries to dlelete other members messages
@pytest.mark.skip('Not yet implemented')
def test_edit_acess_error_dms(clear_server, get_user_1, auth_id_v2):
    dm_id_dict = requests.post(config.url + 'dm/create/v1', json= {
        'token': get_user_1['token'], 
        'u_ids': [auth_id_v2["auth_user_id"]]
    }).json()

    dm_id = dm_id_dict['dm_id']

    message_dict = (requests.post(config.url + 'message/senddm/v1', json = {
        'token': get_user_1['token'],
        'dm_id': dm_id,
        'message': 'Hello there' }).json())    

    message_id = message_dict['message_id']

    assert requests.delete(config.url + 'message/remove/v1', json = {
        'token' : auth_id_v2['token'],
        'message_id': message_id
    }).status_code == 400





