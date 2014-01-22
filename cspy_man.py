import sys

from flask import Flask
from flask import request

import simplejson
import requests
from subprocess import CalledProcessError, check_output

from github_payload import github_payload
from cspy_conf import cspy_conf
from mailer import mailer
from template_parser import template_parser

import datetime

''' Load Configuration '''
conf = cspy_conf('cspy_man.conf.ini')
current_time = datetime.datetime.now()

app = Flask(__name__)

@app.route('/')
def index():
	app.logger.debug(request)	
	return 'Welcome to CS Python Course Manager'

'''
Hook to Deploy Course Website
'''
@app.route('/deploy', methods=['GET', 'POST'])
def deploy():
	if request.method == 'POST':
		''' POST Request processing '''
		#Parse GitHub payload
		post_data = simplejson.loads(request.form['payload'])
		##Uncomment for local testing
		##post_data = simplejson.loads(request.data)
		##app.logger.debug(post_data)
		payload = github_payload(post_data)
		
		''' Execute deployment script '''
		try:
			#app.logger.debug('SCRIPT: {}'.format(conf.scripts['remote_deploy']))
			output = check_output(['bash', conf.scripts['remote_deploy']])
			
			
		except CalledProcessError as e:
			#app.logger.debug('[ERROR]: {}'.format(e))
			output = '[PROCESS_ERROR] {}'.format(e)
		except:
			output = '[OS_ERROR] {}'.format(sys.exc_info()[0])
		
		#Prepare & Send Deployment Email
		tags = {}
		tags['TIMESTAMP'] = current_time.strftime("%Y-%m-%d %I:%M%p %Z")
		tags['REPO_URL'] = payload.repo_url
		tags['REPO_NAME'] = '{}/{}'.format(payload.repo_org, payload.repo_name)
		tags['COMMIT_ID'] = payload.commit_id
		tags['COMMIT_URL'] = payload.commit_url
		tags['COMMIT_TIMESTAMP'] = payload.commit_timestamp
		tags['AUTHOR_NAME'] = payload.author_name
		tags['AUTHOR_EMAIL'] = payload.author_email
		tags['GH_USERNAME'] = payload.author_gh_username
		tags['SCRIPT_LOG'] = output.replace('\n', '<br/>').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
		
		tp = template_parser(conf.templates['website_deploy'])
		tp.replace(tags)
		
		mailrequest = {
			'key': '{}'.format(conf.mandrill_api),
			'message': {
				'subject': '{}'.format(tp.get_subject()),
				'html'   : '{}'.format(tp.get_body()),
			
				'from_email': '{}'.format(conf.email_from_email),
				'from_name' : '{}'.format(conf.email_from_name),
			
				'to': [
					{
						'email': '{}'.format(payload.author_email),
						'name' : '{}'.format(payload.author_name),
					}
				],
			
				'headers': {
					'Reply-To': '{}'.format(conf.email_replyto)
				},
			},
		}
		
		r = requests.post('https://mandrillapp.com/api/1.0/messages/send.json', data=simplejson.dumps(mailrequest))
		rres = simplejson.loads(r.content)
		if rres is not None and rres[0]['status'] != 'sent':
			print '[ERROR][MANDRILL][{}] {} - {}'.format(rres[0]['status'], rres[0]['reject_reason'], rres[0]['email'])
		
		
		return 'POST request processed, check logs'
	
	else:
		''' GET Request processing '''
		return 'GET request not supported'

'''
Hook to log commit messages from GitHub
'''
@app.route('/log', methods=['GET', 'POST'])
def log():
	if request.method == 'POST':
		#Parse GitHub payload
		#post_data = simplejson.loads(request.form['payload'])
		##Uncomment for local testing
		post_data = simplejson.loads(request.data)
		##app.logger.debug(post_data)
		payload = github_payload(post_data)
		
		#for c in payload.commits:
			
		
		
		return 'POST request processed, check logs'
	else:
		''' GET Request processing '''
		return 'GET request not supported'



if __name__ == '__main__':
	#app.debug = True
	#app.host = '0.0.0.0'
	app.run()

