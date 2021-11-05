import pytest
import requests
import json
import flask
from src import config

import pytest
from src.other import clear_v1

'''
notifications/get/v1
Return the user's most recent 20 notifications, ordered from most recent to least recent.


Get 
Parameters:{ token }

Return Type:{ notifications }

List of dictionaries, where each dictionary contains types { channel_id, dm_id, notification_message } 
where channel_id is the id of the channel that the event happened in, and is -1 if it is being sent to a DM. 
dm_id is the DM that the event happened in, and is -1 if it is being sent to a channel. 
Notification_message is a string of the following format for each trigger action:
      
        tagged: "{User’s handle} tagged you in {channel/DM name}: {first 20 characters of the message}"
        reacted message: "{User’s handle} reacted to your message in {channel/DM name}"
        added to a channel/DM: "{User’s handle} added you to {channel/DM name}"

'''


# Fixture to reset json store before every test
@pytest.fixture
def clear():
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

def test_channel_notif_tagged_and_added(clear, get_user_1, auth_id_v2):
    channel_id_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'sta wars', 'is_public': True}).json()
    
    channel_id = channel_id_dict['channel_id']

    requests.post(config.url + 'channel/invite/v2', json={'token': get_user_1['token'], 'channel_id': channel_id, 'u_id': auth_id_v2['auth_user_id']})

    requests.post(config.url + 'message/send/v1', json = {
        'token': get_user_1['token'],
        'channel_id': channel_id,
        'message': 'Hello there @johnsmith'})
    
    notification_dictionary = requests.get(config.url + 'notifications/get/v1', params = {'token': auth_id_v2['token']}).json()

    assert notification_dictionary['notifications'] == [{
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in sta wars: Hello there @johnsmi"
    }, 
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone added you to sta wars"
    }]

def test_channel_notif_tagged_edited(clear, get_user_1, auth_id_v2):
    channel_id_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'sta wars', 'is_public': True}).json()
    
    channel_id = channel_id_dict['channel_id']

    requests.post(config.url + 'channel/invite/v2', json={'token': get_user_1['token'], 'channel_id': channel_id, 'u_id': auth_id_v2['auth_user_id']})

    message_dict = requests.post(config.url + 'message/send/v1', json = {
        'token': get_user_1['token'],
        'channel_id': channel_id,
        'message': 'Hello there GENERAL KENOBI'}).json()
    message_id = message_dict['message_id']

    requests.put(config.url + 'message/edit/v1', json = {
        'token' : get_user_1['token'],
        'message_id': message_id,
        'message' : "Hello there @johnsmith"
    })
    notification_dictionary = requests.get(config.url + 'notifications/get/v1', params = {'token': auth_id_v2['token']}).json()

    assert notification_dictionary['notifications'] == [{
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in sta wars: Hello there @johnsmi"
    }, 
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone added you to sta wars"
    }]

def test_channel_notif_tagged_invalid(clear, get_user_1, auth_id_v2):
    channel_id_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'sta wars', 'is_public': True}).json()
    
    channel_id = channel_id_dict['channel_id']

    requests.post(config.url + 'message/send/v1', json = {
        'token': get_user_1['token'],
        'channel_id': channel_id,
        'message': 'Hello there @johnsmith'})
    
    notification_dictionary = requests.get(config.url + 'notifications/get/v1', params = {'token': auth_id_v2['token']}).json()

    assert notification_dictionary['notifications'] == []


@pytest.mark.skip
# testing that the correct notfications appear for a react to a message
def test_channel_notif_reacted(clear, get_user_1, auth_id_v2):
    channel_id_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'sta wars', 'is_public': True}).json()
    channel_id = channel_id_dict['channel_id']

    requests.post(config.url + 'channel/invite/v2', json={'token': get_user_1['token'], 'channel_id': channel_id, 'u_id': auth_id_v2['auth_user_id']})

    message_dict = requests.post(config.url + 'message/send/v1', json = {
        'token': get_user_1['token'],
        'channel_id': channel_id,
        'message': 'Hello there GENERAL KENOBI'}).json()
    message_id = message_dict["message_id"]

    requests.post(config.url + "message/react/v1", json = {'token': auth_id_v2['token'], 'message_id': message_id, 'react_id': 1})
    
    notification_dictionary = requests.get(config.url + 'notifications/get/v1', params = {'token': get_user_1['token']}).json()
    print(notification_dictionary)
    assert notification_dictionary['notifications'] == [{
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "johnsmith reacted to your message in sta wars"
    }]

def test_dm_notif_tagged_edited(clear, get_user_1, auth_id_v2):
    dm_dict = requests.post(config.url + 'dm/create/v1', json={
        'token': get_user_1['token'], 
        'u_ids': [auth_id_v2['auth_user_id']]
    }).json()

    dm_id = dm_dict['dm_id']

    message_dict = requests.post(config.url + 'message/senddm/v1', json = {
        'token': get_user_1['token'],
        'dm_id': dm_id,
        'message': 'Hello there GENERAL KENOBI'}).json()

    message_id = message_dict['message_id']

    requests.put(config.url + 'message/edit/v1', json = {
        'token' : get_user_1['token'],
        'message_id': message_id,
        'message' : "Hello there @johnsmith"
    })
    
    notification_dictionary = requests.get(config.url + 'notifications/get/v1', params = {'token': auth_id_v2['token']}).json()
    print(notification_dictionary)
    assert notification_dictionary['notifications'] == [{
        'channel_id': -1,
        'dm_id' : dm_id,
        'notification_message' : "ownerone tagged you in johnsmith, ownerone: Hello there @johnsmi"
    }, 
    {
        'channel_id': -1,
        'dm_id' : dm_id,
        'notification_message' : "ownerone added you to johnsmith, ownerone"
    }]

def test_dm_notif_tagged_and_added(clear, get_user_1, auth_id_v2):
    dm_dict = requests.post(config.url + 'dm/create/v1', json={
        'token': get_user_1['token'], 
        'u_ids': [auth_id_v2['auth_user_id']]
    }).json()

    dm_id = dm_dict['dm_id']

    requests.post(config.url + 'message/senddm/v1', json = {
        'token': get_user_1['token'],
        'dm_id': dm_id,
        'message': 'Hello there @johnsmith'})
    
    notification_dictionary = requests.get(config.url + 'notifications/get/v1', params = {'token': auth_id_v2['token']}).json()
    print(notification_dictionary)
    assert notification_dictionary['notifications'] == [{
        'channel_id': -1,
        'dm_id' : dm_id,
        'notification_message' : "ownerone tagged you in johnsmith, ownerone: Hello there @johnsmi"
    }, 
    {
        'channel_id': -1,
        'dm_id' : dm_id,
        'notification_message' : "ownerone added you to johnsmith, ownerone"
    }]

@pytest.mark.skip
def test_dm_notif_reacted(clear, get_user_1, auth_id_v2):
    # Owner invites john smith with triggers a notification for john smith
    dm_dict = requests.post(config.url + 'dm/create/v1', json={
        'token': get_user_1['token'], 
        'u_ids': [auth_id_v2['auth_user_id']]
    }).json()

    dm_id = dm_dict['dm_id']

    message_dict = requests.post(config.url + 'message/senddm/v1', json = {
        'token': get_user_1['token'],
        'dm_id': dm_id,
        'message': 'Hello there GENERAL KENOBI'}).json()

    message_id = message_dict['message_id']

    requests.post(config.url + "message/react/v1", json = {'token': auth_id_v2['token'], 'message_id': message_id, 'react_id': 1})

    # check john smiths notifications
    notification_dictionary = requests.get(config.url + 'notifications/get/v1', params = {'token': auth_id_v2['token']}).json()
    print(notification_dictionary)
    print(f'dm_id {dm_id}')
    assert notification_dictionary['notifications'] == [{
        'channel_id': -1,
        'dm_id' : dm_id,
        'notification_message' : "johnsmith reacted to your message in ownerone, johnsmith"
    }]

@pytest.mark.skip
def test_notifications_many(clear, get_user_1, auth_id_v2):
    channel_id_dict = requests.post(config.url + 'channels/create/v2', json={'token': get_user_1['token'], 'name': 'sta wars', 'is_public': True}).json()
    print(channel_id_dict)
    channel_id = channel_id_dict['channel_id']

    requests.post(config.url + 'channel/invite/v2', json={'token': get_user_1['token'], 'channel_id': channel_id, 'u_id': auth_id_v2['auth_user_id']})

    i = 0
    while i < 30:
        requests.post(config.url + 'message/send/v1', json = {
            'token': get_user_1['token'],
            'channel_id': channel_id,
            'message': 'Hello there @johnsmith'})
        i += 1
    
    message_dict = requests.post(config.url + 'message/send/v1', json = {
        'token': auth_id_v2['token'],
        'channel_id': channel_id,
        'message': 'Hello there GENERAL KENOBI'}).json()

    message_id = message_dict["message_id"]

    requests.post(config.url + "message/react/v1", json = {'token': get_user_1['token'], 'message_id': message_id, 'react_id': 1})

    dm_dict = requests.post(config.url + 'dm/create/v1', json={
        'token': get_user_1['token'], 
        'u_ids': [auth_id_v2['auth_user_id']]
    }).json()

    dm_id = dm_dict['dm_id']

    requests.post(config.url + 'message/senddm/v1', json = {
        'token': get_user_1['token'],
        'dm_id': dm_id,
        'message': 'Hello there @johnsmith'})

    notification_dictionary = requests.get(config.url + 'notifications/get/v1', params = {'token': auth_id_v2['token']}).json()
    print(notification_dictionary)

    assert notification_dictionary['notifications'] == [{
        'channel_id': -1,
        'dm_id' : dm_id,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    }, 
    {
        'channel_id': -1,
        'dm_id' : dm_id,
        'notification_message' : "ownerone added you to ownerone, johnsmith"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    },
    {
        'channel_id': channel_id,
        'dm_id' : -1,
        'notification_message' : "ownerone tagged you in : Hello there @johnsmi"
    }]

@pytest.mark.skip
def test_invalid_token(clear):
    '''
    Tests whether the auth id is invalid.

    Expects: 
        AccessError (403 error)
    '''

    invalid_token = '1000'
    
    invalid_request = requests.get(config.url + 'notifications/get/v1', params = {'token': invalid_token})
    assert (invalid_request.status_code) == 403
