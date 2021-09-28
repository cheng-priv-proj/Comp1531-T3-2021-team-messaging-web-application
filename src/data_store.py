# Dict 1:
#   Key: Email
#   Value: Dictionary {
#          Password, 
#          Auth_id}
# Dict 2:
#   Key: Auth_id
#   Value: Dictionary { 
#          u_id }
# Dict 3:
#   Key: Channel_id:
#   Value: Dictionary {
#          Channel Name
#          Is Public/Private
#          Messages
#          owner_members
#          all_members }
# Dict 4: 
#   (Matches ‘user’ type)
#   Key: u_id:
#   Value: Dictionary {
#          u_id
#          Email
#          Name_first
#          Name_last
#          Handle_str }


## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'email': {},
    'auth_user_id': {},
    'channel_id': {},
    'u_id': {}
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def get_email_dict(self):
        return self.initial_object['email']

    def get_auth_user_id_dict(self):
        return self.initial_object['auth_user_id']
    
    def get_channel_id_dict(self):
        return self.initial_object['channel_id']

    def get_u_id_dict(self):
        return self.initial_object['u_id']

    def get_user_info_from_auth_id(self, auth_id):
        u_id = self.initial_object['auth_user_id'].get(auth_id)
        return self.initial_object['u_id'].get(u_id)

    def check_user_is_member_of_channel(self, channel_id, u_id):
        channel_details = self.get_channel_id_dict().get(channel_id)
        if not any (member['u_id'] == u_id for member in channel_details['all_members']):
            return False
        
        return True

    def update_value(dict_key, key, value):
        self.initial_object[dict_key][key] = value

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()

