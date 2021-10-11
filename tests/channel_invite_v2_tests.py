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
def test_member_invite(clear_server, get_invitee, get_user_1):
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

def test_invite_multiple(clear_server, get_invitee, get_user_1): 
    owner2_user_id = extract_user(auth_register_v1('owner2@test.com', 'password', 'owner', 'two'))
    channel2_id = extract_channel(channels_create_v1(owner2_user_id, 'test channel2', True))
    owner1_user_id = extract_user(register)
    channel1_id = extract_channel(register)

    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))

    channel_invite_v1(owner1_user_id, channel1_id, friend_auth_id)
    channel_invite_v1(owner2_user_id, channel2_id, friend_auth_id)

    assert channels_list_v1(friend_auth_id) == {
        'channels': [
            {
                'channel_id': channel1_id,
                'name': 'test channel'
            }, 
            {
                'channel_id': channel2_id,
                'name': 'test channel2'
            },
        ],
    }
    
def test_private_invite(clear, extract_user, extract_channel):
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
    
def test_invalid_uid(clear, register, extract_user, extract_channel):
    owner_user_id = extract_user(register)
    channel_id = extract_channel(register)
    invalid_friend_auth_id = 10000
    
    with pytest.raises(InputError):
        channel_invite_v1(owner_user_id, channel_id, invalid_friend_auth_id)

def test_invalid_auth_id_and_u_id(clear, register, extract_channel):
    invalid_auth_user_id = 100
    channel_id = extract_channel(register)
    invalid_auth_id = 100

    with pytest.raises(AccessError):
        channel_invite_v1(invalid_auth_user_id, channel_id, invalid_auth_id)

def test_invalid_channel_id(clear, register, extract_user):
    owner_user_id = extract_user(register)
    invalid_channel_id = 100
    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))
    
    with pytest.raises(InputError):
        channel_invite_v1(owner_user_id, invalid_channel_id, friend_auth_id)

def test_already_member(clear, register, extract_user, extract_channel):
    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))
    
    owner_user_id = extract_user(register)
    channel_id = extract_channel(register)

    channel_invite_v1(owner_user_id, channel_id, friend_auth_id)
    with pytest.raises(InputError):
        channel_invite_v1(owner_user_id, channel_id, friend_auth_id)

def test_already_owner(clear, register, extract_user, extract_channel):
    owner_user_id = extract_user(register)
    channel_id = extract_channel(register)

    with pytest.raises(InputError):
        channel_invite_v1(owner_user_id, channel_id, owner_user_id)

def test_unauthorised_invite(clear, register, extract_user, extract_channel):
    notmember_user_id = extract_user(auth_register_v1('member@test.com', 'password', 'member', 'one'))
    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))
    
    channel_id = extract_channel(register)

    with pytest.raises(AccessError):
        channel_invite_v1(notmember_user_id, channel_id, friend_auth_id)

# Test that checks channel list to comfirm successful invite.
def test_is_added(clear, register, extract_user, extract_channel):
    owner_user_id = extract_user(register)
    channel_id = extract_channel(register)
    friend_auth_id = extract_user(auth_register_v1('friend@test.com', 'password', 'friend', 'one'))

    channel_invite_v1(owner_user_id, channel_id, friend_auth_id)

    assert channels_list_v1(friend_auth_id) == {
        'channels': [
        	{
                'channel_id': channel_id,
                'name': 'test channel'
            },
        ],
    }
