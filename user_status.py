import redis_serialized

STATUS_WAIT = 0
STATUS_CONN = 1
STATUS_DCON = 2


class User_status(redis_serialized.Redis_serialized):
    def __init__(self, **kwargs):
        super(User_status, self).__init__('user_status', 'user_count', kwargs)
        self.fields = {'uid' : kwargs.get('uid', ''), \
                           'gender_self' : kwargs.get('gender_self' ''), \
                           'gender_target' : kwargs.get('gender_target', ''), \
                           'lat' : kwargs.get('lat', ''),\
                           'lng': kwargs.get('lng'),\
                           'chat_id' : '',\
                           'status' : STATUS_WAIT
                           }
        self.topics = kwargs.get('topics', '').split(',')

    def store(self, r):
        if self.fields.get('uid', '') == '':
            return False
        else:
            super(User_status, self).store(r)
            r.set('uid_store::' + str(self.fields['uid']), str(self.get_id()))
            add_user(r, str(self.get_id()))
            r.sadd(self.field_str('topic_set'), *tuple(self.topics))
            return True

    def get(self, r):
        super(User_status, self).get(r)
        self.topics = r.smembers(self.field_str('topic_set'))

    @staticmethod
    def set_chat(r, rid, chat_id):
        r.set('user_status::'+str(rid)+'::chat_id', chat_id)

    @staticmethod
    def get_chat(r, rid):
        return r.get('user_status::'+str(rid)+'::chat_id')


    @staticmethod
    def inter_topics(r, rid1, rid2):
        a = r.sinter('user_status::'+str(rid1)+'::topic_set', 'user_status::'+str(rid2)+'::topic_set')
        return a

    @staticmethod
    def store_conn_status(r, rid, new_status):
        r.set('user_status::'+str(rid)+'::status', new_status)

    @staticmethod
    def get_conn_status(r, rid):
        return r.get('user_status::'+str(rid)+'::status')

    @staticmethod
    def get_rid(r, uid):
        return r.get('uid_store::'+str(uid))

    @staticmethod
    def get_uid(r, rid):
        return r.get('user_status::'+str(rid)+'::uid')


def add_user(r, r_id):
    r.lpush('user_id_list', r_id)
    r.lpush('not_conn_list', r_id)

def get_all_users(r):
    return r.lrange('user_id_list', 0, -1)

def get_waiting_users(r):
    return r.lrange('not_conn_list', 0, -1)
