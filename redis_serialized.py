class Redis_serialized(object):
    def __init__(self, name, counter_name, kws):
        if 'obj_id' in kws:
            self.id_valid = True
            self.id = kws['obj_id']
        else:
            self.id = 0
            self.id_valid = False
            
        self.counter_name = counter_name
        self.name = name
        self.fields = {}

    def field_str(self, field):
        return self.name + '::' + str(self.id) + '::' + field

    def store(self, r):
        if (self.counter_name == '')  or (self.name == ''):
            return False
        if self.id_valid == False:
            self.id = r.incr('counters::' + self.counter_name) - 1
            self.id_valid = True

        for (k, v) in self.fields.iteritems():
            r.set(self.field_str(k), v)

        return True

    def get(self, r):
        if self.id_valid == False:
            return False

        new_dict = {}
        for key in self.fields:
            print 'key: ' + str(key)
            new_dict[key] = r.get(self.field_str(key))

        self.fields = new_dict

    def get_id(self):
        if self.id_valid:
            return self.id
        else:
            return -1

            

            
            
