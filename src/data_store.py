import json

######### DATASTORE STRUCTURE ##################################################
#  
# login:
#   key: email
#   value: dict {
#           password, 
#           auth_user_id 
#           } 
#
# tokens:
#   key: token (str)
#   value: u_id
#
# channels:
#   key: channel_id:
#   value: dict {
#               name
#               is_public
#               owner_members
#               all_members 
#               }
#
# dms:
#   key: dm_id:
#   value: dict {
#               details : { name, members}
#               creator 
#               }
#
# message ids:
#   key: message_id
#   value: channel_id or dm_id
# 
# messages:
#   (dm_ids must be negative, channel_ids must be positive)
#   key: channel_id or dm_id
#   value: [message]
#               
# users: 
#   (matches ‘user’ type)
#   key: u_id:
#   value: dict {
#               u_id
#               email
#               name_first
#               name_last
#               handle_str
#               }
#
# permissions:
#   key: u_id
#   value: { 1 or 2 }
#
# message_count: num_messages
#
################################################################################

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

class Datastore:

    # Initialisation and Resetting Methods #####################################
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
                'perms' : {},
                'message_count': 0
            }, 
            FILE
            )

        # re initialise the datastore
        self.__init__()

    def update_json(self):
        with open('src/json_dump/data_store.txt', 'w') as FILE:
            json.dump(self.__store, FILE)

    # Get Methods ##############################################################

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
        return self.get_u_ids_from_token_dict().get(token)

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

    def get_channels_or_dms_id_from_message_id_dict(self):
        return self.__store['message_ids']

    def get_channel_or_dm_id_from_message_id(self, message_id):
        return self.get_channels_or_dms_id_from_message_id_dict().get(message_id)

    def get_messages_from_channel_or_dm_id_dict(self):
        return self.__store['messages']
  
    def get_messages_from_channel_or_dm_id(self, id):
        return self.get_messages_from_channel_or_dm_id_dict().get(id)

    def get_message_from_message_id(self, message_id):
        channel_or_dm_id = self.get_channel_or_dm_id_from_message_id(message_id)

        messages = self.get_messages_from_channel_or_dm_id(channel_or_dm_id)
        return next((message for message in messages if message['message_id'] == message_id), None)

    def get_messages_count(self):
        return self.__store['message_count']

    # users

    def get_users_from_u_id_dict(self):
        return self.__store['users']

    def get_user_from_u_id(self, u_id):
        return self.get_users_from_u_id_dict().get(u_id)

    def get_user_perms_from_u_id_dict(self):
        return self.__store['perms']

    def get_user_perms_from_u_id(self, u_id):
        return self.get_user_perms_from_u_id_dict().get(u_id)

    def get_num_streams_owners(self):
        perms = self.get_user_perms_from_u_id_dict().items()
        return len([u_id for u_id, perm_id in perms if perm_id == 1])

    # Check Methods ############################################################

    def is_token_invalid(self, token):
        if token in self.get_u_ids_from_token_dict():
            return False
        return True

    def is_user_member_of_channel(self, channel_id, u_id):
        channels = self.get_channels_from_channel_id_dict().get(channel_id)
        if not any (member['u_id'] == u_id for member in channels['all_members']):
            return False
        
        return True
    
    def is_user_member_of_dm(self, dm_id, u_id):
        members = self.get_dm_from_dm_id(dm_id).get('members')

        if not any (member['u_id'] == u_id for member in members):
            return False
        
        return True

    def is_user_member_of_channel_or_dm(self, channel_or_dm_id, u_id):
        if channel_or_dm_id <= -1:
            return self.is_user_member_of_dm(channel_or_dm_id, u_id)
        
        return self.is_user_member_of_channel(channel_or_dm_id, u_id)

    def is_user_sender_of_message(self, auth_user_id, message_id):
        message = self.get_message_from_message_id(message_id)
        if message.get('u_id') == auth_user_id:
            return True

        return False

    def is_invalid_message_id(self, message_id):
        messages = self.get_channels_or_dms_id_from_message_id_dict()
        if message_id not in messages:
            return True
        
        return False
        
    def is_channel_owner(self, channel_id, u_id):
        owners = self.get_channels_from_channel_id_dict().get(channel_id).get('owner_members')
        if not any (member.get('u_id') == u_id for member in owners):
            return False
             
        return True   

    def is_channel_only_owner(self, channel_id):
        channels = self.get_channels_from_channel_id_dict().get(channel_id)
        if len(channels.get('owner_members')) == 1:
            return True 
        
        return False

    def is_user_owner_of_channel_or_dm(self, channel_or_dm_id, u_id):
        if channel_or_dm_id < 0:
            return self.get_dm_creator_from_dm_id(channel_or_dm_id) == u_id
        
        return self.is_channel_owner(channel_or_dm_id, u_id) 

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

    def is_duplicate_handle(self, handle):
        users = self.get_users_from_u_id_dict()
        if any (user.get('handle_str') == handle for user in users.values()):
            return True

        return False

    def is_invalid_user_id(self, u_id):
        users = self.get_users_from_u_id_dict()

        if u_id not in users:
            return True

        if users.get(u_id).get('email') == '':
            return True
        
        return False
    
    # returns True even if user is removed
    def is_invalid_profile(self, u_id):
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

    def insert_channel_owner(self, channel_id, u_id):
        self.get_channel_from_channel_id(channel_id).get('owner_members').append(data_store.get_user_from_u_id(u_id))

    def insert_dm(self, creator, dm_id, u_ids, name):
        self.get_dms_from_dm_id_dict()[dm_id] = {
            'details' : {'name': name, 'members': u_ids},
            'creator' : creator
        }
        self.get_messages_from_channel_or_dm_id_dict()[dm_id] = []
        self.update_json()

    def insert_message(self, id, message):
        self.get_messages_from_channel_or_dm_id(id).insert(0, message)
        self.get_channels_or_dms_id_from_message_id_dict()[message.get('message_id')] = id
        self.update_json()

    def update_value(self, dict_key, key, value):
        self.__store[dict_key][key] = value
        self.update_json()

    # Remove ###################################################################

    def remove_message(self, message_id):
        channel_or_dm_id = self.get_channel_or_dm_id_from_message_id(message_id)
        self.get_messages_from_channel_or_dm_id(channel_or_dm_id).remove(self.get_message_from_message_id(message_id))
        del self.get_channels_or_dms_id_from_message_id_dict()[message_id]
        self.update_json()

    # Other ####################################################################

    def invalidate_token(self, token):
        tokens = self.get_u_ids_from_token_dict()
        del tokens[token]
        self.update_json()
    
    def update_name(self, auth_user_id, name_first, name_last):
        user = self.get_users_from_u_id_dict().get(auth_user_id)
        user['name_first'] = name_first
        user['name_last'] = name_last

        self.update_json()
    
    def update_email(self, auth_user_id, email):
        user = self.get_users_from_u_id_dict().get(auth_user_id)
        login_info = self.get_logins_from_email_dict()
        old_email = user['email']

        login_info[email] = login_info.pop(old_email)
        user['email'] = email

        self.update_json()
    
    def update_handle(self, auth_user_id, handle):
        user = self.get_users_from_u_id_dict().get(auth_user_id)
        user['handle_str'] = handle

        self.update_json()

    def remove_dm(self, dm_id):
        dm = self.get_dm_from_dm_id(dm_id)
        dm['members'] = []

        self.update_json()
        
    def increment_message_count(self):
        self.__store['message_count'] += 1

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store
    
    def remove_channel_owner(self, channel_id, u_id):
        channels = self.get_channels_from_channel_id_dict().get(channel_id)
        members = channels['owner_members']
    
        for person in members:
            if person['u_id'] == u_id:
                members.remove(person)
        
        self.update_json()

    def admin_user_remove(self, u_id):
        user = self.get_user_from_u_id(u_id)

        # remove login info
        login = self.get_logins_from_email_dict()
        email = user['email']
        del login[email]

        # invalidate all tokens
        tokens = self.get_u_ids_from_token_dict().items()
        self.__store['token'] = {token: user_id for token, user_id in tokens if user_id != u_id}

        # loop through channel to delete user from all channels
        channels = self.get_channels_from_channel_id_dict()
        for c_id in channels:
            for member in channels[c_id]['all_members']:
                if member['u_id'] == u_id:
                    channels[c_id]['all_members'].remove(member)

            for member in channels[c_id]['owner_members']:
                if member['u_id'] == u_id:
                    channels[c_id]['owner_members'].remove(member)
        
        # loop through dms to delete user from all dms
        dms = self.get_dms_from_dm_id_dict()
        for dm_id in dms:
            for member in dms[dm_id]['details']['members']:
                if member['u_id'] == u_id:
                    dms[dm_id]['details']['members'].remove(member)        

        # replace the users messages
        messages = data_store.get_messages_from_channel_or_dm_id_dict()
        for dm_or_channel_id in messages:
            for message in messages[dm_or_channel_id]:
                if message['u_id'] == u_id:
                    message['message'] = 'Removed user'

        # remove user permissions
        del self.get_user_perms_from_u_id_dict()[u_id]

        # Update user/profile
        user['email'] = ''
        user['name_first'] = 'Removed'
        user['name_last'] = 'user'
        user['handle_str'] = ''

        self.update_json()

print('Loading Datastore...')

global data_store
data_store = Datastore()
