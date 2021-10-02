# Login:
#   Key: email
#   Value: Dictionary {
#          password, 
#          auth_id } 
# U_id:
#   Key: auth_id
#   Value: Dictionary { 
#          u_id }
# Channels:
#   Key: channel_id:
#   Value: Dictionary {
#          channel: {
#              name
#              is_public
#              owner_members
#              all_members }
# Messages:
#   Key: channel_id
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
#   Value: {global_id : 1 or 2}

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'login': {},
    'u_id': {},
    'channels': {},
    'messages' : {},
    'users': {},
    'perms' : {}
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def get_login_from_email_dict(self):
        return self.__store['login']

    def get_u_id_from_auth_dict(self):
        return self.__store['u_id']
    
    def get_channels_from_channel_id_dict(self):
        return self.__store['channels']

    def get_messages_from_channel_id_dict(self):
        return self.__store['messages']

    def get_users_from_u_id_dict(self):
        return self.__store['users']

    def get_user_info_from_auth_id(self, auth_id):
        u_id = self.__store['u_id'].get(auth_id)
        return self.__store['users'].get(u_id['u_id'])

    def get_user_perms_from_u_id_dict(self):
        return self.__store['perms']

    # Assumes valid input
    def check_user_is_member_of_channel(self, channel_id, u_id):

        channel_details = self.get_channels_from_channel_id_dict().get(channel_id)
        if channel_id != None and not any (member['u_id'] == u_id for member in channel_details['all_members']):
            return False
        
        return True
    
    def isStreamOwner(self, u_id):
        return self.get_user_perms_from_u_id_dict().get(u_id) == 1

    def isValid_auth_user_id(self, auth_user_id):
        u_id_dict = self.get_u_id_from_auth_dict()
        if auth_user_id not in u_id_dict:
            return False
        
        return True
    
    def insert_u_id(self, u_id, auth_id):
        self.get_u_id_from_auth_dict()[auth_id] = {
            'u_id': u_id
        }

    def insert_login(self, email, password, auth_id):
        self.get_login_from_email_dict()[email] = {
            'password': password,
            'auth_id': auth_id
        }

    def insert_user_info(self, u_id, email, name_first, name_last, handle_str):
        self.get_users_from_u_id_dict()[u_id] = {
            'u_id': u_id,
            'email': email,
            'name_first': name_first,
            'name_last': name_last,
            'handle_str': handle_str
        }
    
    def insert_user_perm(self, u_id, global_id):
        self.get_user_perms_from_u_id_dict()[u_id] = {
            'global_id' : global_id
        }
    
    # TODO: change this after using new function below
    def insert_channel(self, channel_id, channel_name, is_public, messages, owner_members, all_members):
        self.get_channels_from_channel_id_dict()[channel_id] = {
            'name': channel_name,
            'is_public': is_public,
            'owner_members': owner_members,
            'all_members': all_members,
        }
        # note that messages is a list of dicts, pls ensure channel_messages accounts for this
        self.get_messages_from_channel_id_dict()[channel_id] = messages

    def update_value(self, dict_key, key, value):
        self.__store[dict_key][key] = value

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()

