import json

# Login:
#   Key: email
#   Value: Dictionary {
#          password, 
#          auth_user_id } 
#
# Tokens:
#   Key: token (str)
#   Value: u_id
#
# Channels:
#   Key: channel_id:
#   Value: Dictionary {
#              name
#              is_public
#              owner_members
#              all_members }
#
# DMs:
#   Key: dm_id:
#   Value: Dictionary {
#              details : { name, members}
#              owner_members }
#
# Message ids:
#   Key: message_id
#   Value: channel_id or dm_id
# 
# Messages:
#   (dm_ids must be negative)
#   Key: channel_id or dm_id
#   Value: [message]
#               
# Users: 
#   (Matches ‘user’ type)
#   Key: u_id:
#   Value: Dictionary {
#          u_id
#          Email
#          Name_first
#          Name_last
#          Handle_str }
#
# Permissions:
#   Key: u_id
#   Value: { 1 or 2 }

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'login' : {},
    'token' : {},
    'channels' : {},
    'dms': {},
    'message_ids' : {},
    'messages' : {},
    'users': {},
    'perms' : {},
    'message_count': 0
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

class Datastore:
    def __init__(self):
        with open('src/json_dump/data_store.txt', 'r') as FILE:
            self.__store = json.load(FILE)

    def hard_reset(self):
        # replace json dump with a fresh copy of datastore
        with open('src/json_dump/data_store.txt', 'w') as FILE:
            json.dump(
            {
                'login' : {},
                'token' : {},
                'channels' : {},
                'dms': {},
                'message_ids' : {},
                'messages' : {},
                'users': {},
                'perms' : {}
            }, 
            FILE
            )

        # re initialise the datastore
        self.__init__()

    def update_json(self):
        with open('src/json_dump/data_store.txt', 'w') as FILE:
            json.dump(self.__store, FILE)

    # Get Functions ############################################################
    def get(self):
        return self.__store

    # login

    def get_logins_from_email_dict(self):
        return self.__store['login']
    
    def get_login_from_email(self, email):
        return self.get_logins_from_email_dict().get(email)
    
    # tokens

    def get_u_ids_from_token_dict(self):
        return self.__store['token']

    def get_u_id_from_token(self, token):
        check_none = self.get_u_ids_from_token_dict().get(token)

        return -1 if check_none == None else check_none

    # channels

    def get_channels_from_channel_id_dict(self):
        return self.__store['channels']

    def get_channel_from_channel_id(self, channel_id):
        return self.get_channels_from_channel_id_dict().get(channel_id)
    
    # dms

    def get_dms_from_dm_id_dict(self):
        return self.__store['dms']

    def get_dm_from_dm_id(self, dm_id):
        return self.get_dms_from_dm_id_dict().get(dm_id).get('details')

    def get_dm_creator_from_dm_id(self, dm_id):
        return self.get_dms_from_dm_id_dict().get(dm_id).get('creator')

    # messages

    def get_channel_or_dm_id_from_message_id_dict(self):
        return self.__store['message_ids']

    def get_channel_or_dm_id_from_message_id(self, message_id):
        return self.get_channel_or_dm_id_from_message_id_dict().get(message_id)

    def get_messages_from_channel_or_dm_id_dict(self):
        return self.__store['messages']
  
    def get_messages_from_channel_or_dm_id(self, id):
        return self.get_messages_from_channel_or_dm_id_dict().get(id)

    def get_message_from_message_id(self, message_id):
        channel_or_dm_id = self.get_channel_or_dm_id_from_message_id(message_id)
        message = {}
        for messages in data_store.get_messages_from_channel_or_dm_id(channel_or_dm_id):
            if messages['message_id'] == message_id:
                message = messages
        
        return message

    def get_messages_count(self):
        return self.__store['messages']

    # users

    def get_users_from_u_id_dict(self):
        return self.__store['users']

    def get_user_from_u_id(self, u_id):
        return self.get_users_from_u_id_dict().get(u_id)

    def get_user_perms_from_u_id_dict(self):
        return self.__store['perms']

    def get_user_perms_from_u_id(self, u_id):
        return self.get_user_perms_from_u_id_dict().get(u_id)


    # Check functions ##########################################################

    def is_token_invalid(self, token):
        if token in self.get_u_ids_from_token_dict():
            return False
        return True

    def is_user_member_of_channel(self, channel_id, u_id):
        channel = self.get_channel_from_channel_id(channel_id)
        if not any (member['u_id'] == u_id for member in channel['all_members']):
            return False
        
        return True
        
    def is_user_member_of_dm(self, dm_id, u_id):
        dm = self.get_dm_from_dm_id(dm_id)
        if u_id not in dm.get('details').get('members'):
            return False
        
        return True

    def is_user_member_of_dm_or_channel(self, channel_or_dm_id, u_id):
        if channel_or_dm_id <= -1:
            return self.is_user_member_of_dm(channel_or_dm_id, u_id)
        
        return self.is_user_member_of_channel(channel_or_dm_id)

    def is_user_owner_of_channel_or_dm(self, channel_or_dm_id, u_id):
        if channel_or_dm_id <= -1:
            if u_id == self.get_dm_creator_from_dm_id(channel_or_dm_id):
                return True
            
            return False
        
        channel = self.get_channel_from_channel_id(channel_or_dm_id)
        if any (member['u_id'] == u_id for member in channel['owner_members']):
            return True

        return False
        
    def is_user_sender_of_message(self, auth_user_id, message_id):
        message = self.get_message_from_message_id(message_id)
        if message.get('u_id') == auth_user_id:
            return True

        return False

    def is_stream_owner(self, u_id):
        return self.get_user_perms_from_u_id_dict().get(u_id) == 1

    def is_invalid_email(self, email):
        emails = self.get_logins_from_email_dict()
        if email not in emails:
            return True
        
        return False

    def is_duplicate_email(self, email):
        emails = self.get_logins_from_email_dict()
        if email in emails:
            return True
        
        return False

    def is_invalid_user_id(self, u_id):
        users = self.get_users_from_u_id_dict()
        if u_id not in users:
            return True
        
        return False

    def is_invalid_channel_id(self, channel_id):
        channels = self.get_channels_from_channel_id_dict()
        if channel_id not in channels:
            return True
        
        return False

    def is_invalid_dm_id(self, dm_id):
        dms = self.get_dms_from_dm_id_dict()
        if dm_id not in dms:
            return True
        
        return False

    def is_invalid_message_id(self, message_id):
        messages = self.get_channel_or_dm_id_from_message_id_dict()
        if message_id not in messages:
            return True
        
        return False

    # Insertion functions ######################################################

    def insert_login(self, email, password, auth_id):
        self.get_logins_from_email_dict()[email] = {
            'password': password,
            'auth_id': auth_id
        }
        self.update_json()

    def insert_token(self, token, auth_user_id):
        self.get_u_ids_from_token_dict()[token] = auth_user_id
        self.update_json()

    def insert_user(self, u_id, email, name_first, name_last, handle_str):
        self.get_users_from_u_id_dict()[u_id] = {
            'u_id': u_id,
            'email': email,
            'name_first': name_first,
            'name_last': name_last,
            'handle_str': handle_str
        }
        self.update_json()
    
    def insert_user_perm(self, u_id, global_id):
        self.get_user_perms_from_u_id_dict()[u_id] = global_id
        self.update_json()

    def insert_channel(self, channel_id, channel_name, is_public, messages, owner_members, all_members):
        self.get_channels_from_channel_id_dict()[channel_id] = {
            'name': channel_name,
            'is_public': is_public,
            'owner_members': owner_members,
            'all_members': all_members,
        }

        self.get_messages_from_channel_or_dm_id_dict()[channel_id] = messages
        self.update_json()

    def insert_dm(self, owner_members, dm_id, u_ids, name):
        self.get_dms_from_dm_id_dict()[dm_id] = {
            'details' : {'name': name, 'members': u_ids},
            'owner_members' : owner_members
        }
        self.get_messages_from_channel_or_dm_id_dict()[dm_id] = []
        self.update_json()

    def insert_message(self, id, message):
        self.get_messages_from_channel_or_dm_id(id).insert(0, message)
        self.get_channel_or_dm_id_from_message_id_dict()[message.get('message_id')] = id
        self.update_json()
        
    def insert_message_count(self):
        self.__store['message_count'] += 1

    def update_value(self, dict_key, key, value):
        self.__store[dict_key][key] = value
        self.update_json()

    # Remove ###################################################################

    def remove_message(self, message_id):
        channel_or_dm_id = self.get_channel_or_dm_id_from_message_id(message_id)
        del self.get_channel_or_dm_id_from_message_id_dict()[message_id]

        self.get_messages_from_channel_or_dm_id(channel_or_dm_id).remove(self.get_message_from_message_id(message_id))

    # Other ####################################################################

    def invalidate_token(self, token):
        tokens = self.get_u_ids_from_token_dict()
        del tokens[token]

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()

