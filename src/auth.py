from src.data_store import data_store
from src.error import InputError
from src.other import check_type, check_email_valid
from src.other import handle_str_generation
from src.other import stream_owner, stream_member
from src.other import hash_str
from src.config import SECRET, EMAIL, PASSWORD
import re
import jwt
import smtplib
from email.message import EmailMessage

def auth_login_v1(email, password):
    '''
    Given the email and password of a registered user, returns the corresponding
    auth_id.
    Arguments:
        email       (string)   - users email
        password    (string)   - users password

    Exceptions:
        TypeError  - occurs when email or password given are not strings
        InputError - occurs when email does not belong to a user
        InputError - occurs when password is not correct

    Return value:
        Returns {token, auth_user_id} on success
    '''

    check_type(email, str)
    check_type(password, str)
    
    if data_store.is_invalid_email(email):
        raise InputError ('email does not belong to a user')
    
    login = data_store.get_login_from_email(email)

    if hash_str(password) != login.get('password'):
        raise InputError ('password is not correct')

    auth_user_id = login.get("auth_id")

    token = jwt.encode({
                'auth_user_id': auth_user_id,
                'token_count': len(data_store.get_u_ids_from_token_dict())
                },
                 SECRET, algorithm='HS256')

    data_store.insert_token(token, auth_user_id)

    return { 'token': token,'auth_user_id': auth_user_id }

def auth_register_v1(email, password, name_first, name_last):
    '''
    Updates data store with a new user's information
    Generates a u_id, auth_id and handle_str.

    Arguments:
        email       (string)    - users email
        password    (string)    - users password
        name_first  (string)    - users first name
        name_last   (string)    - users last name

    Exceptions:
        TypeError   - occurs when email, password, name_first or name_last
                    are not strings
        InputError  - occurs when email is not a valid email
        InputError  - occurs when email is already being used by another user
        InputError  - occurs when password is less than 6 characters
        InputError  - occurs when name_first is less than 1 character
                    or more than 50
        InputError  - occurs when name_last is less than 1 character
                    or more than 50

    Return value:
        Returns {auth_user_id} on success
    '''

    # checking for valid input types
    check_type(email, str)
    check_type(password, str)
    check_type(name_first, str)
    check_type(name_last, str)

    check_email_valid(email)

    # check for valid password, name_first and name_last lengths
    if len(password) < 6:
        raise InputError ('password is less than 6 characters')
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError ('name_first is less than 1 character or more than 50')
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError ('name_last is less than 1 character or more than 50')
    
    # check if email is already being used
    if data_store.is_duplicate_email(email):
        raise InputError ('email is already being used by another user')

    # generate a unique auth_id
    auth_user_id = len(data_store.get_users_from_u_id_dict())
    handle_str = handle_str_generation(name_first, name_last)

    # hash the password
    encrypted_password = hash_str(password)

    # insert new data into dicts
    perm = stream_owner if auth_user_id == 0 else stream_member
    data_store.insert_user(auth_user_id, email, name_first, name_last, handle_str)
    data_store.insert_user_perm(auth_user_id, perm)
    data_store.insert_login(email, encrypted_password, auth_user_id)

    return { 'auth_user_id': auth_user_id }


def auth_logout_v1(token):
    '''
    Given an active token, invalidates the token to log the user out.

    Arguments:
        token           (str) - unique user token

    Exceptions:
        N/A

    Return value:
        Returns {} on success
    '''

    data_store.invalidate_token(token)

    return {}

def auth_passwordreset_request_v1(email):
    '''
    Given an email address, if the user is a registered user, sends them an
    email containing a specific secret code, that when entered in
    auth/passwordreset/reset, shows that the user trying to reset the password
    is the one who got sent this email. No error should be raised when passed an
    invalid email, as that would pose a security/privacy concern. When a user
    requests a password reset, they should be logged out of all current sessions.
    
    note that an email has been created for this function:

    email       : 1531isbriansfavsubject@gmail.com
    password    : 1531brain

    Arguments:
        email           (str) - email str

    Exceptions:
        N/A

    Returns {} on success
    '''
    check_type(email, str)

    if data_store.is_invalid_email(email):
        return

    reset_code = email

    email_msg = EmailMessage()
    email_msg.set_content(email)

    email_msg['Subject'] = 'Did you recieve it? My message?'
    email_msg['From'] = EMAIL
    email_msg['To'] = reset_code

    # Send message via a SMTP server.
    s = smtplib.SMTP("smtp.gmail.com", 587)

    s.ehlo()
    s.starttls()
    s.login(EMAIL, PASSWORD)

    s.send_message(email_msg)
    s.close()

    auth_user_id = data_store.get_login_from_email(email).get('auth_id')

    # store reset code
    data_store.insert_reset_code(reset_code, auth_user_id)

    all_tokens = data_store.get_u_ids_from_token_dict()

    tokens = [token for token in all_tokens if all_tokens[token] == auth_user_id]

    for token in tokens:
        auth_logout_v1(token)

    return {}

# Using this implementation, what happens if the user accidentally guesses another user's reset code?
# Big security issue, and large bug
def auth_passwordreset_reset_v1(reset_code, new_password):
    '''
    Given a reset code for a user, set that user's new password to the
    password provided.
    
    Arguments:
        reset_code      (str) - secret reset string
        new_password    (str) - new password string

    Exceptions:
        TypeError   - occurs when reset_code, new_password are not strs
        InputError  - reset_code is not a valid reset code
        InputError  - password entered is less than 6 characters long

    Return {} on success
    '''

    if type(new_password) != str:
        raise TypeError

    print(new_password)
    if len(new_password) < 6:
        raise InputError

    if data_store.is_reset_code_invalid(reset_code) == True:
        raise InputError

    u_id = data_store.get_u_id_from_reset_code(reset_code)

    encrypted_password = hash_str(new_password)
    data_store.update_password(u_id, encrypted_password)

    data_store.remove_reset_code(reset_code)

    return {}