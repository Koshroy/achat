import redis_serialized

STATUS_WAIT = 0
STATUS_CONN = 1
STATUS_DCON = 2


class Chat_data(redis_serialized.Redis_serialized):
    def __init__(self, **kwargs):

        super(Chat_data, self).__init__('chat_data', 'chat_count', kwargs)
        self.fields = {'uid_a' : kwargs.get('uid_a', ''), 'uid_b' : kwargs.get('uid_b', ''), 'status' : kwargs.get('status', STATUS_DCON)}


    def store(self, r):
        if (self.fields['uid_a'] == '') or (self.fields['uid_b'] == '') or (self.fields['status'] == -1):
            return False
        else:
            return super(Chat_data, self).store(r)

    def add_uid(self, uid):
        r.set('uid::'+uid+'::chat', self.id)

    @staticmethod
    def get_both_uids(r, cid):
        id_str = 'chat_data::'+str(cid)+'::'
        ret_list = []
        ret_list.append(r.get(id_str+'uid_a'))
        ret_list.append(r.get(id_str+'uid_b'))
        return ret_list

    @staticmethod
    def get_conn_status(r, cid):
        return r.get('chat_data::'+str(cid)+'::status')

    @staticmethod
    def set_conn_status(r, cid, status):
        r.set('chat_data::'+str(cid)+'::status', status)
