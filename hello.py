from flask import Flask, url_for, render_template, session, escape, request, redirect, g, jsonify
from contextlib import closing
from random import choice
import os, sqlite3, xmpp, string
import redis
import user_status, chat_data

DATABASE = '/Users/koshroy/tmp/achat.db'
SECRET_KEY = 'Z;t\x02\x9eB\x91\xac\xd3\x98\xd8\xc6\xbc@%\xda\x95\x13\xaeJ\xed"\xcfT'
DEBUG = True

STATUS_WAIT = 0
STATUS_CONN = 1
STATUS_DCON = 2

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def connect_xmpp(j):
    c = xmpp.Client(j, debug=[])
    c.connect()
    return c

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def gen_id():
    return ''.join([choice(string.letters + string.digits) for i in range(20)])

# @app.before_request
# def before_request():
#     g.r = connect_r()

# @app.teardown_request
# def teardown_request(exception):
#     if hasattr(session, 'xmpp_conn'):
#         session.xmpp_conn.disconnect()

@app.route('/chat')
def chat():
    session['uniq_id'] = gen_id()
    return render_template('chatwin.html', uid=session.get('uniq_id', 'abcd'), user=session.get('username', None))

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        session['topics'] = request.form.get('topics', '')
        session['name'] = request.form.get('name', '')
        session['gender-self'] = request.form.get('gender-self', '')
        session['gender-target'] = request.form.get('gender-target', '')
        session['lat'] = request.form.get('lat', '')
        session['lng'] = request.form.get('lng', '')
        return redirect(url_for('chat'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['user']
        session['uniq_id'] = gen_id()
        return redirect(url_for('hello_world'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    del session['username']
    del session['uniq_id']
    return redirect(url_for('hello_world'))


@app.route('/sendmsg', methods=['POST'])
def sendmsg():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    uid = request.form['uniq_id']
    if user_status.User_status.get_conn_status(r, uid) == STATUS_DCON:
        return 'disconnected'
    user_status.User_status.get_chat(r, uid)
    rid = user_status.User_status.get_rid(r, uid)
    cid = user_status.User_status.get_chat(r, rid)

    rid_list = chat_data.Chat_data.get_both_uids(r, cid)
    #uid_list = [user_status.User_status.get_uid(r, rid_list[0]), user_status.User_status.get_uid(r, rid_list[1])]
    uid_list =  map(lambda rid: user_status.User_status.get_uid(r, str(rid)), chat_data.Chat_data.get_both_uids(r, cid))
    if uid_list[0] == uid:
        to_uid = uid_list[1]
    else:
        to_uid = uid_list[0]

    jid = xmpp.protocol.JID(uid+'@localhost')
    x = xmpp.Client(jid.getDomain(), debug=[])
    x.connect()
    xmpp.features.getRegInfo(x, jid.getDomain(), sync=True)
    reg_succ = xmpp.features.register(x, jid.getDomain(),
                                      {'username':jid.getNode(),
                                       'password':'abcd'})
    x.auth(jid.getNode(), 'abcd')
    x.send(xmpp.protocol.Message(to_uid+'@localhost', request.form['message']))
    x.disconnect()
    return 'registered? ' + str(reg_succ) + '\n' + request.form['uniq_id']+'@localhost'


    

@app.route('/recvmsg', methods=['POST'])
def recvmsg():
    uid = request.form['uniq_id']
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    rid = user_status.User_status.get_rid(r, uid)
    c_status = user_status.User_status.get_conn_status(r, rid)
    if (c_status == str(STATUS_DCON)):
        return jsonify(msg='event', text='stopped')
    jid = xmpp.protocol.JID(uid+'@localhost')
    x = xmpp.Client(jid.getDomain(), debug=[])
    x.connect()
    xmpp.features.getRegInfo(x, jid.getDomain(), sync=True)
    reg_succ = xmpp.features.register(x, jid.getDomain(),
                                      {'username':jid.getNode(),
                                       'password':'abcd'})
    x.auth(jid.getNode(), 'abcd')
    session['r_msg'] = ''
    x.RegisterHandler('message', messageCB)
    x.sendInitPresence(requestRoster=0)
    x.Process(1)
    x.disconnect()
    return jsonify(msg='chat', text=session.get('r_msg', ''))
    


    
    

@app.route('/chatconnect', methods=['POST'])
def chatConn():
    uid = request.form['uniq_id']
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    if request.form['req'] == 'start':
        rid = user_status.User_status.get_rid(r, uid)
        if rid is None:
            u = user_status.User_status(uid=uid, gender_self=session.get('gender-self', ''), gender_target=session.get('gender-target', ''), lat=session.get('lat', ''), lng=session.get('lng', ''))
            u.store(r)
            return 'waiting'

        w_users = user_status.get_waiting_users(r)
        if rid in w_users:
            return 'waiting'

        status = int(user_status.User_status.get_conn_status(r, rid))
        if status == STATUS_DCON:
            return 'stopped'
        elif status == STATUS_CONN:
            return 'connected'
        else:
            return 'herped: ' + str(status)
    elif request.form['req'] == 'stop':
        rid = user_status.User_status.get_rid(r, uid)
        if rid is None:
            return 'error'
        else:
            rid = int(rid)
            cid = user_status.User_status.get_chat(r, rid)
            rid_list = chat_data.Chat_data.get_both_uids(r, cid)
            for rid_chat in rid_list:
                user_status.User_status.store_conn_status(r, rid_chat, STATUS_DCON)
            chat_data.Chat_data.set_conn_status(r, cid, STATUS_DCON)
            return 'success'

def messageCB(conn, msg):
    session['r_msg'] = msg.getBody()

### Test handlers        

@app.route('/formtest')
def formTest():
    topics = request.args.get('topics', '').split(',')

@app.route('/ttest')
def template_test():
    return render_template('test_home.html')

        
if __name__ == "__main__":
    app.run()
