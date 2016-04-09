# oauth PRAW template by /u/The1RGood #
#==================================================Imports=========================================================
import time, praw
import webbrowser
from flask import Flask, request
from threading import Thread

#==================================================Config Params===================================================
subreddit = 'subreddit_name'

karma_requirement = 1

acceptance_message = 'You have been approved.'

rejection_message = 'You do not have enough karma.'

ignored_users = [
	'reddit',
	'automoderator'
]
#==================================================End Config======================================================
#==================================================OAUTH APPROVAL==================================================
app = Flask(__name__)

CLIENT_ID = '' #SET THIS TO THE ID UNDER PREFERENCES/APPS
CLIENT_SECRET = '' #SET THIS TO THE SECRET UNDER PREFERENCES/APPS
scope = 'identity read modcontributors privatemessages' #SET THIS. SEE http://praw.readthedocs.org/en/latest/pages/oauth.html#oauth-scopes FOR DETAILS.
#These permissions should be enough, though.

REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

#Kill function, to stop server once auth is granted
def kill():
	func = request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('Not running with the Werkzeug Server')
	func()
	return "Shutting down..."

#Callback function to receive auth code
@app.route('/authorize_callback')
def authorized():
	global access_information
	state = request.args.get('state', '')
	code = request.args.get('code', '')
	r.get_access_information(code)
	user = r.get_me()
	text = 'Bot successfully started on account /u/'+user.name
	kill()
	return text
	
r = praw.Reddit('OAuth FLASK Template Script'
                'https://praw.readthedocs.org/en/latest/'
                'pages/oauth.html for more info.')
r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
webbrowser.open(r.get_authorize_url('DifferentUniqueKey',scope,True))
app.run(debug=False, port=65010)
#==================================================END OAUTH APPROVAL-=============================================

print('Loading subreddit...')
cc = r.get_subreddit(subreddit)

print('Loading contrib list...')
contribs = cc.get_contributors(limit=None)
names = []
for c in contribs:
	names+=[c.name]
	
for n in ignored_users:
	names+=[n]
	
def push_to_seen(m):
	seen.insert(0,m)
	if(len(seen)>100):
		seen.pop()

print('Buffering old mail...')
seen = []
mail = cc.get_mod_mail(limit=50)
for m in mail:
	push_to_seen(m.name)
		
print('Scanning...')
running = True
while(running):
	try:
		mail = cc.get_mod_mail(limit=50)
		for m in mail:
			if(m.name not in seen):
				push_to_seen(m.name)
				karma = max(m.author.link_karma,m.author.comment_karma)
				if(karma >= karma_requirement and m.author.name not in names):
					cc.add_contributor(m.author.name)
					m.reply(acceptance_message)
					names+=[m.author.name]
					print('Adding user : ' + m.author.name)
				elif(m.author.name not in names):
					m.reply(rejection_message)
		time.sleep(300)
	except KeyboardInterrupt:
		running = False
	except Exception as e:
		pass
		
print('Shutting down')