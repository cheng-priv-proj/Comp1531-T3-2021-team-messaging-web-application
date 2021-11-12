import pytest
import requests
import json
import flask
from requests.models import Response
from src import config

from src.other import clear_v1


@pytest.fixture
def clear_server():
    '''
    Clears the datastore.
    '''
    requests.delete(config.url + "clear/v1")

@pytest.fixture
def get_user_1():
    '''
    Fixture to register someone and returns a dictionary of {token, auth_user_id}
    '''
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'owner@test.com', 
        'password': 'spotato', 
        'name_first': 'owner', 
        'name_last' : 'one'
        })
    return response.json()

@pytest.fixture
def auth_id_v2():
    '''
    Fixture to register someone and returns a dictionary of {token, auth_user_id}
    '''
    response = requests.post(config.url + 'auth/register/v2', json={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    return response.json()

def test_normal_case_channel(clear_server, get_user_1):
    '''
    Standard test with owner case

    Expects: 
        Correct output from channel/messages.
    '''

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
    
    message_dict = requests.get(config.url + 'channel/messages/v2', params = {
        'token': get_user_1['token'],
        'channel_id': extracted_channel_id, 
        'start': 0 }).json()

    assert message_dict == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

def test_normal_case_non_owner(clear_server, get_user_1, auth_id_v2):
    '''
    Standard test with non owner case

    Expects: 
        Correct output from channel/messages.
    '''

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
    
    message_dict = requests.get(config.url + 'channel/messages/v2', params = {
        'token': auth_id_v2['token'],
        'channel_id': extracted_channel_id, 
        'start': 0 }).json()

    assert message_dict == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

def test_owner_perms(clear_server, get_user_1, auth_id_v2):
    '''
    Testing owner can edit other peoples messages

    Expects: 
        Correct output from channel/messages.
    '''

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
    
    message_dict = requests.get(config.url + 'channel/messages/v2', params = {
        'token': get_user_1['token'],
        'channel_id': extracted_channel_id, 
        'start': 0 }).json()

    assert message_dict == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }


def test_invalid_message_id(clear_server, get_user_1):
    '''
    Case where message_id does not refer to a valid message within a channel/DM that the authorised user has joined

    Expects: 
        InputError (400 error)
    '''

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


def test_user_is_not_member(clear_server, get_user_1, auth_id_v2):
    '''
    Case where user is not in the  channel/DM that the authorised user has joined.

    Expects: 
        InputError (400 error)
    '''

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

    assert requests.delete(config.url + 'message/remove/v1', json = {
        'token' : auth_id_v2['token'],
        'message_id': message_dict['message_id']
    }).status_code == 400

def test_edit_acess_error(clear_server, get_user_1, auth_id_v2):
    '''
    AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:
      
        the message was sent by the authorised user making this request
        the authorised user has owner permissions in the channel/DM

    Expects: 
        AccessError (403 error)
    '''

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
    }).status_code == 403

def test_normal_case_dms(clear_server, get_user_1, auth_id_v2):
    '''
    Standard test with owner case

    Expects: 
        Correct output from dm/messages.
    '''

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

    message_dict = requests.get(config.url + 'dm/messages/v1', params = {
        'token': get_user_1['token'],
        'dm_id': dm_id, 
        'start': 0 }).json()

    assert message_dict == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

def test_normal_case_non_owner_dms(clear_server, get_user_1, auth_id_v2):
    '''
    Standard test with non owner case

    Expects: 
        Correct output from dm/messages.
    '''

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

    message_dict = requests.get(config.url + 'dm/messages/v1', params = {
        'token': auth_id_v2['token'],
        'dm_id': dm_id, 
        'start': 0 }).json()

    assert message_dict == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

def test_owner_perms_dms(clear_server, get_user_1, auth_id_v2):
    '''
    Testing owner can edit other peoples messages

    Expects: 
        Correct output from dm/messages.
    '''

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

    message_dict = requests.get(config.url + 'dm/messages/v1', params = {
        'token': get_user_1['token'],
        'dm_id': dm_id, 
        'start': 0 }).json()

    assert message_dict == {
        'messages': [], 
        'start': 0, 
        'end': -1
    }

def test_invalid_message_id_dms(clear_server, get_user_1, auth_id_v2):
    '''
    Case where message_id does not refer to a valid message within a channel/DM that the authorised user has joined

    Expects: 
        InputError (400 error)
    '''

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

def test_edit_acess_error_dms(clear_server, get_user_1, auth_id_v2):
    '''
    AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:
      
        the message was sent by the authorised user making this request
        the authorised user has owner permissions in the channel/DM

    Expects: 
        AccessError (403 error)
    '''
    
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
    }).status_code == 403





