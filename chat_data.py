import redis_serialized

class Chat_data(redis_serialized.Redis_serialized):
    def __init__(self, **kwargs):

        super(Chat_data, self).__init__('chat_data', 'chat_count', kwargs)
        self.fields = {'uid_a' : kwargs.get('uid_a', ''), 'uid_b' : kwargs.get('uid_b', ''), 'status' : kwargs.get('status', '')}


    def store(self, r):
        if (self.fields['uid_a'] == '') or (self.fields['uid_b'] == '') or (self.fields['status'] == -1):
            return False
        else:
            return super(Chat_data, self).store(r)

    def add_uid(self, uid):
        r.set('uid::'+uid+'::chat', self.id)

