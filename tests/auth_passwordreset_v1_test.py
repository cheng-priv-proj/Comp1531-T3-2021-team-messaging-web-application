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

def test_successful_password_reset(clear, register_user, new_email):
    # Create a user
    register_user(new_email.email_address)

    requests.post(url + 'auth/passwordreset/request/v1', json = {
        'email': new_email.email_address
    }

    with mailslurp_client.ApiClient(configuration) as api_client:
        waitfor_controller = mailslurp_client.WaitForControllerApi(api_client)
        email = waitfor_controller.wait_for_latest_email(inbox_id=new_email.id, timeout=30000, unread_only=True)
    
    requests.post(url + 'auth/passwordreset/reset/v1', json = {
        'reset_code': email.subject,
        'new_password': 'new_password'
    })

    assert requests.post(url + 'auth/login/v2', json = {
        'email': new_email.email_address,
        'password': 'new_password'
    }).status_code == 200

def test_invalid_reset_code(clear, register_user, new_email):
    # Create a user
    register_user(new_email.email_address)
    invalid_reset_code = ''

    assert requests.post(url + 'auth/passwordreset/reset/v1', json = {
        'reset_code': invalid_reset_code,
        'new_password': 'new_password'
    }).status_code == 400

def test_password_too_short(clear, register_user, new_email):
    # Create a user
    register_user(new_email.email_address)

    requests.post(url + 'auth/passwordreset/request/v1', json = {
        'email': new_email.email_address
    }

    with mailslurp_client.ApiClient(configuration) as api_client:
        waitfor_controller = mailslurp_client.WaitForControllerApi(api_client)
        email = waitfor_controller.wait_for_latest_email(inbox_id=new_email.id, timeout=30000, unread_only=True)
    
    assert requests.post(url + 'auth/passwordreset/reset/v1', json = {
        'reset_code': email.subject,
        'new_password': 'short'
    }).status_code == 400

