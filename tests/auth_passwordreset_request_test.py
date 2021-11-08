import pytest
import requests
import mailslurp_client

from src.config import url

configuration = mailslurp_client.Configuration()
# Pls don't hack jk unless you know what you're doing :D 
# Gon be buggy asf glhf 
configuration.api_key['x-api-key'] = "6c91d6e6e7970c0bff72eeb53a79cc29a7d50e2c158015ebb4fcdd45ee203f75"

# Clears storage 
@pytest.fixture
def clear():
    requests.delete(url + "clear/v1")

# Creates a channel using the given details and returns the channel_id
@pytest.fixture
def register_channel():
    def register_channel_function(token, name, is_public):
        channel_details = {
            'token': token,
            'name': name,
            'is_public': is_public
        }
        channel_id_dict = requests.post(url + 'channels/create/v2', json = channel_details).json()
        channel_id = channel_id_dict.get('channel_id')

        return channel_id
    return register_channel_function

# Create an owner and some users
@pytest.fixture 
def register_user():
    def register_user_function(email):
        user_details = {
            'email': email,
            'password': 'password', 
            'name_first': 'some',
            'name_last': 'user'
        }
        details_dict = requests.post(url + 'auth/register/v2', json = user_details).json()

        return details_dict
    return register_user_function

@pytest.fixture
def new_email():
    with mailslurp_client.ApiClient(configuration) as api_client:

        # create an inbox using the inbox controller
        api_instance = mailslurp_client.InboxControllerApi(api_client)
        inbox = api_instance.create_inbox()

        # check the id and email_address of the inbox
        assert len(inbox.id) > 0
        assert "mailslurp.com" in inbox.email_address
    
    return inbox

def test_secret_code_sent(clear, new_email, register_user):
    register_user(new_email.email_address)

    requests.post(url + 'auth/passwordreset/request/v1', json = {
        'email': new_email.email_address
    })

    with mailslurp_client.ApiClient(configuration) as api_client:
        waitfor_controller = mailslurp_client.WaitForControllerApi(api_client)
        email = waitfor_controller.wait_for_latest_email(inbox_id=new_email.id, timeout=30000, unread_only=True)

def test_logged_out(clear, new_email, register_channel, register_user):
    token = register_user(new_email.email_address)
    register_channel(token, 'channel', True)

    requests.post(url + 'auth/passwordreset/request/v1', json = {
        'email': new_email.email_address
    })
    
    assert requests.post(url + 'channels/create/v2', json = {
        'token': token,
        'name': 'channel2',
        'is_public': True
    }).status_code == 403
    