import pytest
import requests
import imaplib
from email.header import decode_header
import email

from src.config import url

gmail = 'comp1531receive@gmail.com'
password = 'EAGLE13A'
gmail_host= 'imap.gmail.com'

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
def get_most_recent_code():
    def new_email_function():
        mail = imaplib.IMAP4_SSL(gmail_host)
        mail.login(gmail, password)
        status, messages = mail.select("INBOX")
        assert status == 'OK'
        messages = int(messages[0])
        
        status, msg = mail.fetch(str(messages - 1), "(RFC822)")
        assert status == 'OK'
        for response in msg:
            if isinstance(response, tuple):
                message = email.message_from_bytes(response[1])
                body = message.get_payload()
        
        return body.strip()
    return new_email_function

def test_successful_password_reset(clear, register_user, get_most_recent_code):
    register_user(gmail)
    requests.post(url + 'auth/passwordreset/request/v1', json = {
        'email': gmail
    })
    
    body = get_most_recent_code()
    
    requests.post(url + 'auth/passwordreset/reset/v1', json = {
        'reset_code': body,
        'new_password': 'new_password'
    })
    
    assert requests.post(url + 'auth/login/v2', json = {
        'email': gmail,
        'password': 'new_password'
    }).status_code == 200

def test_invalid_reset_code(clear, register_user):
    # Create a user
    register_user(gmail)
    invalid_reset_code = ''

    assert requests.post(url + 'auth/passwordreset/reset/v1', json = {
        'reset_code': invalid_reset_code,
        'new_password': 'new_password'
    }).status_code == 400

def test_password_too_short(clear, register_user, get_most_recent_code):
    # Create a user
    register_user(gmail)

    requests.post(url + 'auth/passwordreset/request/v1', json = {
        'email': gmail
    })

    body = get_most_recent_code()
    
    assert requests.post(url + 'auth/passwordreset/reset/v1', json = {
        'reset_code': body,
        'new_password': 'short'
    }).status_code == 400

