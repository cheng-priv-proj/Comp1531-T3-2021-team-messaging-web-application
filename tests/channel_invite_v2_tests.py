import pytest

from src.channel import channel_details_v1, channel_invite_v1

from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channels import channels_list_v1
from src.channel import channel_join_v1

from src.other import clear_v2
from src.error import InputError
from src.error import AccessError

import requests
import json
import flask
from src import config

# Important Accessarror case
# In the spec, it spacifies an access error when 'channel_id is valid and the authorised user is not a member of the channel'
# Howver in this iteration, auth id is not a parameter for this function. 


#NEED TO IMPLEMENT CLEAR v2 or change clear v1
@pytest.fixture
def clear_server():
    clear_v2()

@pytest.fixture
def get_user_1():
    response = requests.post(config.url + 'auth/register/v2', data={
        'email': 'owner@test.com', 
        'password': 'spotato', 
        'name_first': 'owner', 
        'name_last' : 'one'
        })
    return response.json()

def get_invitee():
    response = requests.post(config.url + 'auth/register/v2', data={
        'email': 'example@email.com', 
        'password': 'potato', 
        'name_first': 'John', 
        'name_last' : 'smith'
        })
    return response.json()

# TEsting that inviting someone shows up in channel details
def test_member_invite_v2(clear_server, get_invitee, get_user_1):
    channel_dict = requests.post(config.url + 'channels/create/v2', data={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    requests.post(config.url + 'channel/invite/v2', data={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'u_id': get_invitee['auth_user_id']}).json()
    details = requests.get(config.url + 'channel/details/v2', params={'token': get_user_1['token'], 'channel_id': extracted_channel_id}).json()

    assert details["all_members"] == [
        {
            'u_id': get_user_1['auth_user_id'],
            'email': 'owner@test.com',
            'name_first': 'owner',
            'name_last': 'one',
            'handle_str': 'ownerone'
        },
        {
            'u_id': get_invitee['auth_user_id'],
            'email': 'example@email.com',
            'name_first': 'John',
            'name_last': 'smith',
            'handle_str': 'Johnsmith'
        }
    ]

# Checks that multiple users can be invited to a channel also owner and members both have invite perms
def test_invite_multiple_v2(clear_server, get_invitee, get_user_1): 
    channel_dict = requests.post(config.url + 'channels/create/v2', data={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    response = requests.post(config.url + 'auth/register/v2', data={
        'email': 'eexample@email.com', 
        'password': 'pootato', 
        'name_first': 'Johno', 
        'name_last' : 'smith'
        })
    user_3_dict = response.json()

    requests.post(config.url + 'channel/invite/v2', data={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'u_id': get_invitee['auth_user_id']}).json()
    requests.post(config.url + 'channel/invite/v2', data={'token': get_invitee['token'], 'channel_id': extracted_channel_id, 'u_id': user_3_dict['auth_user_id']}).json()

    details = requests.get(config.url + 'channel/details/v2', params={'token': get_user_1['token'], 'channel_id': extracted_channel_id}).json()
    assert details["all_members"] == [
        {
            'u_id': get_user_1['auth_user_id'],
            'email': 'owner@test.com',
            'name_first': 'owner',
            'name_last': 'one',
            'handle_str': 'ownerone'
        },
        {
            'u_id': get_invitee['auth_user_id'],
            'email': 'example@email.com',
            'name_first': 'John',
            'name_last': 'smith',
            'handle_str': 'Johnsmith'
        },
        {
            'u_id': user_3_dict['auth_user_id'],
            'email': 'eexample@email.com',
            'name_first': 'Johno',
            'name_last': 'smith',
            'handle_str': 'Johnosmith'
        }
    ]
    
def test_private_invite(clear_server, get_invitee, get_user_1):
    channel_dict = requests.post(config.url + 'channels/create/v2', data={'token': get_user_1['token'], 'name': 'test channel', 'is_public': False}).json()
    extracted_channel_id = channel_dict['channel_id']

    requests.post(config.url + 'channel/invite/v2', data={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'u_id': get_invitee['auth_user_id']}).json()
    details = requests.get(config.url + 'channel/details/v2', params={'token': get_user_1['token'], 'channel_id': extracted_channel_id}).json()

    assert details["all_members"] == [
        {
            'u_id': get_user_1['auth_user_id'],
            'email': 'owner@test.com',
            'name_first': 'owner',
            'name_last': 'one',
            'handle_str': 'ownerone'
        },
        {
            'u_id': get_invitee['auth_user_id'],
            'email': 'example@email.com',
            'name_first': 'John',
            'name_last': 'smith',
            'handle_str': 'Johnsmith'
        }
    ]

# Uid is not an existing uid
def test_invalid_uid(clear_server, get_user_1):
    channel_dict = requests.post(config.url + 'channels/create/v2', data={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']
    fake_u_id = 42424242
    response = requests.post(config.url + 'channel/invite/v2', data={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'u_id': fake_u_id}).json()
    assert(response.status_code == 400)


def test_invalid_channel_id(clear_server, get_invitee, get_user_1):
    bad_channel_id = 5000000
    response = requests.post(config.url + 'channel/invite/v2', data={'token': get_user_1['token'], 'channel_id': bad_channel_id, 'u_id': get_invitee['auth_user_id']}).json()
    assert(response.status_code == 400)

# U_id is already in the channel
def test_already_member(clear_server, get_invitee, get_user_1):
    channel_dict = requests.post(config.url + 'channels/create/v2', data={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    requests.post(config.url + 'channel/invite/v2', data={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'u_id': get_invitee['auth_user_id']}).json()
    response = requests.post(config.url + 'channel/invite/v2', data={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'u_id': get_invitee['auth_user_id']}).json()
    assert(response.status_code == 400)


# Owner tries to join again
def test_already_owner(clear_server, get_invitee, get_user_1):
    channel_dict = requests.post(config.url + 'channels/create/v2', data={'token': get_user_1['token'], 'name': 'test channel', 'is_public': True}).json()
    extracted_channel_id = channel_dict['channel_id']

    #makes user 2 joins so they can send an invite to the owner 
    requests.post(config.url + 'channel/invite/v2', data={'token': get_user_1['token'], 'channel_id': extracted_channel_id, 'u_id': get_invitee['auth_user_id']}).json()
    
    response = requests.post(config.url + 'channel/invite/v2', data={'token': get_invitee['token'], 'channel_id': extracted_channel_id, 'u_id': get_user_1['auth_user_id']}).json()
    assert(response.status_code == 400)


def test_unauthorised_invite(clear, register, extract_user, extract_channel):
    notmember_user_id = extract_user(auth_register_v1('member@test.com', 'password', 'member', 'one'))
    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))
    
    channel_id = extract_channel(register)

    with pytest.raises(AccessError):
        channel_invite_v1(notmember_user_id, channel_id, friend_auth_id)
