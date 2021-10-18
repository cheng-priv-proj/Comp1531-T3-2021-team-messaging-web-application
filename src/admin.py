from src.data_store import data_store
from src.error import InputError









'''

admin/userpermission/change/v1
Given a user by their user ID, set their permissions to new permissions described by permission_id.

POST

Parameters:
    { token, u_id, permission_id }

Return Type:
    {}

InputError when any of:
      
        u_id does not refer to a valid user
        u_id refers to a user who is the only global owner and they are being demoted to a user
        permission_id is invalid
      
AccessError when:
      
        the authorised user is not a global owner

'''







'''
admin/user/remove/v1

Given a user by their u_id, remove them from the Streams. 
This means they should be removed from all channels/DMs, and will not be included in the list of users returned by users/all. 
Streams owners can remove other Streams owners (including the original first owner). 
Once users are removed, the contents of the messages they sent will be replaced by 'Removed user'. 
Their profile must still be retrievable with user/profile, however name_first should be 'Removed' and name_last should be 'user'. 
The user's email and handle should be reusable.

DELETE

Parameters:
    { token, u_id }

Return Type:
    {}


InputError when any of:
      
        u_id does not refer to a valid user
        u_id refers to a user who is the only global owner

AccessError when:
      
        the authorised user is not a global owner

'''