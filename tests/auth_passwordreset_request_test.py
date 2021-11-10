import pytest
import requests
import imaplib
import email

from src.config import url

gmail = 'comp1531receive@gmail.com'
password = 'EAGLE13A'
gmail_host= 'imap.gmail.com'

# Clears storage 
@pytest.fixture
def clear():
    requests.delete(url + "clear/v1")

# Creates a channel using the given details and returns the channel_id
@pytest.fixture
def register_channel():
    def register_channel_function(token, name, is_public):
        print(token)
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

        return details_dict['token']
    return register_user_function

@pytest.fixture
def number_of_emails():
    def new_email_function():
        mail = imaplib.IMAP4_SSL(gmail_host)
        mail.login(gmail, password)
        mail.select("INBOX")
        type, data = mail.search(None, 'ALL')
        
        assert type == 'OK'
        
        mail_ids = data[0]
        id_list = mail_ids.split()
        return len(id_list)
    return new_email_function


def test_secret_code_sent(clear, number_of_emails, register_user):
    register_user(gmail)
    
    len_emails_before_request = number_of_emails()

    requests.post(url + 'auth/passwordreset/request/v1', json = {
        'email': gmail
    })
    
    len_emails_after_request = number_of_emails()
    
    assert (len_emails_before_request + 1) == len_emails_after_request

def test_invalid_email(clear, register_user):
    register_user('notanemail')

def test_logged_out(clear, register_channel, register_user):
    token = register_user(gmail)

    register_channel(token, 'channel', True)

    requests.post(url + 'auth/passwordreset/request/v1', json = {
        'email': gmail
    })
    
    assert requests.post(url + 'channels/create/v2', json = {
        'token': token,
        'name': 'channel2',
        'is_public': True
    }).status_code == 403
    

