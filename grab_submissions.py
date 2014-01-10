import sys

import simplejson
from subprocess import CalledProcessError, check_output

from github_payload import github_payload
from cspy_conf import cspy_conf
#from mailer import mailer
from github import github
from template_parser import template_parser

import datetime

from dateutil import tz
from pprint import pprint
from submission import submission
import csv
import time

import requests
import mandrill

import traceback


def convertTime(time_string):
	utc = datetime.datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%SZ')
	utc = utc.replace(tzinfo=tz.gettz('UTC'))
	return utc.astimezone(tz.gettz('America/Los_Angeles'))

''' Load Configuration '''
conf = cspy_conf('cspy_man.conf.ini')
mandrill_client = mandrill.Mandrill(conf.mandrill_api)

''' Initialize Scripts '''
current_time = datetime.datetime.now()
filestring_time = current_time.strftime('%Y%m%d%H%M%S')
gh = github(conf.github_username, conf.github_password)
ssubmissions = {}

''' Read Repo Details '''
repo_file = 'repos.csv'
rfile  = open(repo_file, 'r')

submodule_file = '{}_{}.submodule.log'.format(repo_file, filestring_time)
sfile  = open(submodule_file, 'w')

reader = csv.reader(rfile)
row_count = 0
for row in reader:
	if len(row) == 0:
		continue;
	
	elif row[0].strip().startswith("#"):
		continue;
	else:
		row_count = row_count + 1
		if row_count == 1:
			continue
		else:
			res = {}
			try:
				ss = submission()
				ss.last_name = row[0].strip()
				ss.first_name = row[1].strip()
				ss.usc_username = row[2].strip()
				ss.github_username = row[3].strip()
				ss.repo_org = row[4].strip()
				ss.repo_name = row[5].strip()
				
				res = gh.get('https://api.github.com/repos/{}/{}/commits'.format(ss.repo_org, ss.repo_name), False)
				ss.commit_sha = res[0]['sha']
				ss.commit_url = res[0]['html_url']
				ss.commit_timestamp = res[0]['commit']['committer']['date']
				ss.commit_message   = res[0]['commit']['message']
				
				if res[0]['committer'] is not None:
					ss.commit_committer = res[0]['committer']['login']
				else:
					ss.commit_committer = 'Your Git Client is Misconfigured'
				ssubmissions[row_count] = ss
				sfile.write('git submodule --quiet add git@github.com:{}/{}.git; cd {}; git fetch --quiet; git checkout --quiet {}; cd ..\n'.format(ss.repo_org, ss.repo_name, ss.repo_name, ss.commit_sha))
			except:
				print '[ERROR][ROW {}] {}'.format(row_count, row)
				#traceback.print_exc()

sfile.close()

''' Send Emails'''
s_count = 0
for s in ssubmissions:
	try:
		#Prepare & Send Submission Email
		tags = {}
		tags['FIRST_NAME'] = ssubmissions[s].first_name
		tags['LAST_NAME'] = ssubmissions[s].last_name
		tags['REPO_NAME'] = ssubmissions[s].repo_name
		tags['USC_USERNAME'] = ssubmissions[s].usc_username
		tags['GH_USERNAME'] = ssubmissions[s].github_username
		tags['REPO_URL'] = '{}/{}'.format(ssubmissions[s].repo_org, ssubmissions[s].repo_name)
		tags['ORG_NAME'] = ssubmissions[s].repo_org
		tags['REPO_NAME'] = ssubmissions[s].repo_name
		tags['COMMIT_URL'] = ssubmissions[s].commit_url
		tags['COMMIT_ID'] = ssubmissions[s].commit_sha
		tags['COMMIT_COMMENT'] = ssubmissions[s].commit_message.encode("utf8")
		tags['COMMIT_TIMESTAMP'] = convertTime(ssubmissions[s].commit_timestamp)
	
		tp = template_parser(conf.templates['confirm_submission'])
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
						'email': '{}@usc.edu'.format(ssubmissions[s].usc_username),
						'name' : '{}{}'.format(ssubmissions[s].first_name, ssubmissions[s].last_name),
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

	except:
		#print ssubmissions[s].__dict__
		print '[ERROR][EMAIL] {} {} <{}@usc.edu>'.format(ssubmissions[s].first_name, ssubmissions[s].last_name, ssubmissions[s].usc_username)

