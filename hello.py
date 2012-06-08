from flask import Flask, url_for, render_template, session, escape, request, redirect, g, jsonify
from contextlib import closing
from random import choice
import os, sqlite3, xmpp, string

DATABASE = '/Users/koshroy/tmp/achat.db'
SECRET_KEY = 'Z;t\x02\x9eB\x91\xac\xd3\x98\xd8\xc6\xbc@%\xda\x95\x13\xaeJ\xed"\xcfT'
DEBUG = True


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
#     return ''

# @app.teardown_request
# def teardown_request(exception):
#     if hasattr(session, 'xmpp_conn'):
#         session.xmpp_conn.disconnect()

@app.route('/')
def hello_world():
    return render_template('main.html', user=session.get('username', None))

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

@app.route('/chat')
def chat():
    session['uniq_id'] = gen_id()
    return render_template('chatwin.html', uid=session.get('uniq_id', 'abcd'), user=session.get('username', None))

@app.route('/sendmsg', methods=['POST'])
def sendmsg():
    db = connect_db()
    pid = request.form['uniq_id']
    db_resp = db.execute("select personaid, personbid, disconnected from chats where personaid='%s' or personbid='%s'"%(pid, pid))
    entries = db_resp.fetchall()
    if len(entries) == 0:
        db.close()
        return 'error'
    to_pid = 'uguuu'
    entry = entries[0]
    if entry[2] == 1:
        db.close()
        return 'disconnected'
    elif entry[0] == pid:
        to_pid = entry[1]
    else:
        to_pid = entry[0]
    db.close()
    jid = xmpp.protocol.JID(pid+'@localhost')
    x = xmpp.Client(jid.getDomain(), debug=[])
    x.connect()
    xmpp.features.getRegInfo(x, jid.getDomain(), sync=True)
    reg_succ = xmpp.features.register(x, jid.getDomain(),
                                      {'username':jid.getNode(),
                                       'password':'abcd'})
    x.auth(jid.getNode(), 'abcd')
    x.send(xmpp.protocol.Message(to_pid+'@localhost', request.form['message']))
    x.disconnect()
    return 'registered? ' + str(reg_succ) + '\n' + request.form['uniq_id']+'@localhost'

@app.route('/recvmsg', methods=['POST'])
def recvmsg():
    pid = request.form['uniq_id']
    db = connect_db()
    db_resp = db.execute("select disconnected from chats where personaid='%s' or personbid='%s'"%(pid, pid))
    entries = db_resp.fetchall()
    if len(entries) != 0:
        dcon_status = entries[0][0]
        db.close()
        if dcon_status == 1:
            return jsonify(msg='event', text='stopped')
    jid = xmpp.protocol.JID(request.form['uniq_id']+'@localhost')
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
    pid = request.form['uniq_id']
    db = connect_db()
    if request.form['req'] == "stop":
        db_resp = db.execute("select id from chats where personaid='%s' or personbid='%s'" %(pid, pid))
        dc_pids = db_resp.fetchall()
        if len(dc_pids) == 0:
            db.close()
            return 'error'
        entry = int(dc_pids[0][0])
        db.execute("update chats set disconnected=1 where id=%d"%entry)
        db.commit()
        db.close()
        return 'success'
    
    db_resp = db.execute("select personaid, personbid, chatopen, disconnected from chats where personaid='%s' or personbid='%s'" %(pid, pid))
    req_pids = db_resp.fetchall()
    if len(req_pids) != 0: # We have a chat with our name registered
        for res in req_pids:
            if res[3] == 1:
                db.close()
                return 'stopped'
            elif res[2] == 0:
                #db.execute("update chats set chatopen=0 where id=%d"%int(res[3]))
                db.close()
                return 'connected'
            else:
                db.close()
                return 'waiting'
    db_resp = db.execute("select * from chats where chatopen=1")
    open_chats = db_resp.fetchall()
    if len(open_chats) == 0:
        db.execute("insert into chats (chatopen, personaid, personbid, gendera, genderb, disconnected) values (1, '%s', '', 0, 0, 0)"%pid)
        db.commit()
        db.close()
        return 'waiting'
    else:
        min_id = min([req[0] for req in open_chats])
        db.execute("update chats set personbid='%s', chatopen=0 where id=%d"%(pid, min_id))
        db.commit()
        db.close()
        return 'connected'
                

def messageCB(conn, msg):
    session['r_msg'] = msg.getBody()
    

        
if __name__ == "__main__":
    app.run()
