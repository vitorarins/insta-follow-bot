from flask import Flask
from flask import render_template
from flask import request, session, url_for, redirect
from flask.ext.socketio import SocketIO, send, emit

from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError

import hmac
from hashlib import sha256

import time, random
import urllib,json,urllib2
# from urllib3 import util
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e0a988c2ef03d31977f017304dbf33c7'
socketio = SocketIO(app)

CLIENT_ID='b0bfe8e2da324814ad5d2c31e4096499'
CLIENT_SECRET='175e2fd04658459382ecd710f7750787'
#APP_URL='http://localhost:8080'
AUTH_TOKEN=''
APP_URL='http://ec2-52-10-129-151.us-west-2.compute.amazonaws.com/'
USERS = [460563723,46983271,11830955,144605776,6860189,7719696,25025320,553762634,202329761,182393608,451573056,1259283205,3122433,144548040]

ips = '52.10.129.151'

signature = hmac.new(CLIENT_SECRET, ips, sha256).hexdigest()
insta_header = '|'.join([ips, signature])

instagram_auth_url='https://api.instagram.com/oauth/access_token'
user_agent = 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7'
headers = { 'User-Agent' : user_agent,
            "Content-type": "application/x-www-form-urlencoded",
            "X-Insta-Forwarded-For": insta_header
            }

instagram_client = InstagramAPI(client_id=CLIENT_ID,
                                       client_secret=CLIENT_SECRET,
                                       redirect_uri=APP_URL)

@app.route('/')
def index():
    auth_code = request.args.get('code')
    username = ''
    
    if auth_code:
        access_token, instagram_user = instagram_client.exchange_code_for_access_token(auth_code)
        username = instagram_user['username']        
        socketio.emit
                                        
    return render_template('index.html',client_id=CLIENT_ID,
                           redirect_uri=APP_URL,
                           username=username)

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message['data'])

    doAllTheFollows(AUTH_TOKEN)
    # t = threading.Timer(1.0, doAllTheFollows)
    # t.start()
    emit('log event', {'data':'I am doing something'})
    

def doAllTheFollows(access_token):

    socketio.emit('log event', {'count': 0, 'data':'I am in!'})
    threading.Timer(120.0, doAllTheFollows).start()
    
    num_unfollows = 0
    
    for user in USERS:
        unfollow_log = "Unfollowing %d" % user
        socketio.emit('log event', {'data':unfollow_log})
        print unfollow_log
        num_unfollows +=unfollow_user(user,access_token)
        # try:
        #     instagram_client.unfollow_user(user)
        #     num_unfollows+=1
        # except InstagramAPIError as e:
        #     error_log = "Error code: %d" % e.status_code
        #     socketio.emit('log event', {'data':error_log})
        #     print error_log

    the_unfollow_log = "Number of users unfollowed is %d" % num_unfollows
    socketio.emit('log event', {'data':the_unfollow_log})
    print the_unfollow_log
        
    time.sleep(60)
        
    num_follows = 0
    for user in USERS:

        follow_log = "Following %d" % user
        socketio.emit('log event', {'data':follow_log})
        print follow_log
        num_follows+= followUser(user,access_token)
        # try:            
        # except InstagramAPIError as e:
        #     error_log = "Error code: %d" % e.status_code
        #     socketio.emit('log event', {'data':error_log})
        #     print error_log            

    the_follow_log = "Number of users followed is %d" % num_follows
    socketio.emit('log event', {'data':the_follow_log})
    print the_follow_log

def followUser(userId,access_token):

    followed=0

    followUrl = "https://api.instagram.com/v1/users/%s/relationship?action=allow"

    values = {'access_token' : access_token,
              'action' : 'follow',
              'client_id' : CLIENT_ID}
    print access_token
    try:
        newFollow = followUrl % (userId)
        socketio.emit('log event', {'data':newFollow})
        print newFollow
        data = urllib.urlencode(values)
        req = urllib2.Request(newFollow,data,headers)
        response = urllib2.urlopen(req)
        result = response.read()
        socketio.emit('log event', {'data':result})        
        print result
        dataObj = json.loads(result);
        followed = 1
                                       
    except Exception, e:
        error_message = e.read()
        socketio.emit('error log', {'code':e.code, 'reason':error_message})
        print error_message
        
    return followed

def unfollow_user(userId,access_token):
    unfollowed=0
    followUrl = "https://api.instagram.com/v1/users/%s/relationship?action=allow"

    values = {'access_token' : access_token,
              'action' : 'unfollow',
              'client_id' : CLIENT_ID}
    print access_token
    try:
        noFollow = followUrl % (userId)
        socketio.emit('log event', {'data':noFollow})        
        print noFollow
        data = urllib.urlencode(values)
        req = urllib2.Request(noFollow,data,headers)
        response = urllib2.urlopen(req)
        result = response.read()
        socketio.emit('log event', {'data':noFollow})                
        print result
        dataObj = json.loads(result)
        unfollowed = 1
        
    except Exception, e:
        error_message = e.read()
        socketio.emit('error log', {'code':e.code, 'reason':error_message})
        print error_message
        
    return unfollowed
    
if __name__ == '__main__':
    socketio.run(app,'0.0.0.0',80)