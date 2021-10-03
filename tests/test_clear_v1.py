import pytest
import sys
 
from src.other import clear_v1

from src.channels import channels_create_v1

from src.auth import auth_register_v1

from src.data_store import data_store
import src.data_store as data_store_file

# Assumes that the data store is initially empty.
# Testing if database is empty by comparing bit size with the bit size of an empty dict.
def test_clearv1_functionality():
    clear_v1()
    empty_data_store = data_store_file.Datastore()
    auth_user_id = auth_register_v1('test@gmail.com', '1234567', 'first', 'last')
    auth_user_id2 = auth_register_v1('test2@gmail.com', '1234567', 'first', 'last')
    auth_id = auth_user_id['auth_user_id']
    auth_id2 = auth_user_id2['auth_user_id']
    channel_id = channels_create_v1(auth_id, 'name', True)
    channel_id2 = channels_create_v1(auth_id2, 'name', True)
    clear_v1()
 
    assert sys.getsizeof(empty_data_store) == sys.getsizeof(data_store)
 
def test_clearv1_returns_empty_dict():
    assert clear_v1() == {}
