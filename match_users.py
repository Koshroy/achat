import redis, user_status, chat_data
import time
import collections

STATUS_WAIT = 0
STATUS_CONN = 1
STATUS_DCON = 2

def main():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    while True:
        try:
            print 'Waiting for user'
            out = r.blpop('not_conn_list', 0)
            print 'out: ' + str(out)
            curr_user = out[1]
            print 'curr_user: ' + str(curr_user)
            print 'wait user: ' + str(user_status.get_waiting_users(r))
            rest_users = user_status.get_waiting_users(r)
            if not isinstance(rest_users, collections.MutableSequence):
                rest_users = list(rest_users[1])
            print 'rest_users: ' + str(rest_users)
            if rest_users == []:
                print 'Found no other waiting users'
                r.lpush('not_conn_list', curr_user)
                time.sleep(0.2)
                continue
            
            print 'Scoring'
            score_list = []
            for u in rest_users:
                score_list.append(score_users(r, curr_user, u))
                print 'Finished scoring'
        # Connect curr_user to user with max score
                match = max(score_list)
                match_ind = score_list.index(match)
                r.lrem('not_conn_list', 0, rest_users[match_ind])

                print 'Match: ' + str(match) + ' Match Index: ' + str(match_ind)
                
                print 'Setting connection status'
                user_status.User_status.store_conn_status(r, curr_user, STATUS_CONN)
                user_status.User_status.store_conn_status(r, match, STATUS_CONN)
                print 'Finished setting connection status'
        except KeyboardInterrupt:
            print 'Quitting'
            exit(0)

def score_users(r, u1, u2):
    sinter = user_status.User_status.inter_topics(r, u1, u2)
    m = len(sinter)
    print 'User a: ' + str(u1) + ' User b: ' + str(u2)
    print 'Greatest match: ' + str(m) + ' Match is: ' + str(sinter)
    return m

if __name__ == "__main__":
    main()

        
