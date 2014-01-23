"""Grab Submissions - Get the submissions in the form of a submodule
 
Grab student submissions from GitHub using the GitHub API
 
Usage:
	grab_submissions.py [-n|--dry-run] <hw_title> <file_name>
    grab_submissions.py [-n|--dry-run] --late <hw_title> <late_file_name>
	grab_submissions.py -h | --help
	grab_submissions.py --version
 
Arguments:
	<file_name>			the file containing the the repository information the file is in csv format (repo-owner, repo-name, github-username)
    <late_file_name>	the file containing the the repository information the file is in csv format (repo-owner, repo-name, issue-number, late-days, grace-period)
	<hw_title>			the name of the hw assignment
 
Options:
	--late			use the late submission behaviour
	-n --dry-run	do not perform any write/push operations to GitHub. Instead log the actions
	-h --help		Show this screen
	--version		Show version
 
"""


import sys

import simplejson
from subprocess import CalledProcessError, check_output

from github_payload import github_payload
from cspy_conf import cspy_conf
from github import github
from template_parser import template_parser

import datetime

from dateutil import tz
from pprint import pprint
from submission import submission
import csv
import time

from docopt import docopt

import requests

import traceback

class submission_type:
	__doc__ = 'ENUM for submission types'
	SUBMITTION_ONTIME = 0
	SUBMITTION_LATE = 1

class submission_info:
	__doc__ = 'Submission details information'
	def __init__(self):
		self.repo_org = None
		self.repo_name = None
		self.repo_user = None
		self.repo_issue = None
		
		self.commit_sha = None
		self.commit_url = None
		self.commit_timestamp = None
		self.commit_message   = None
		
		self.late = None
		self.grace_period = None

def convertTime(time_string):
	utc = datetime.datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%SZ')
	utc = utc.replace(tzinfo=tz.gettz('UTC'))
	return utc.astimezone(tz.gettz('America/Los_Angeles'))



args = docopt(__doc__, version='Grab Submissions v1.0')

''' Load Configuration '''
conf = cspy_conf('cspy_man.conf.ini')

''' Initialize Scripts '''
current_time = datetime.datetime.now()
filestring_time = current_time.strftime('%Y%m%d%H%M%S')
gh = github(conf.github_username, conf.github_password)
ssubmissions = {}

''' Grab and Report On Time Submissions '''
with open(args['<file_name>'], 'r') as repo_file:
	submodule_file = '{}_{}.submodule.log'.format(args['<file_name>'], filestring_time)
	sfile  = open(submodule_file, 'w')

	reader = csv.reader(repo_file)
	row_count = 0
	for row in reader:
		if len(row) == 0:
			continue;
	
		elif row[0].strip().startswith("#"):
			continue;
		else:
			row_count = row_count + 1
			res = {}
			try:
				ss = submission()
				ss.github_username = row[2].strip()
				ss.repo_org = row[0].strip()
				ss.repo_name = row[1].strip()
			
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

''' Create Issues on GitHub '''
s_count = 0
for s in ssubmissions:
	issue = { }
	issue['title'] = 'Submission Confirmation for {}'.format(args['<hw_title>'])
	issue['assignee'] = ssubmissions[s].github_username
	issue['body'] = """At the assignment's deadline, I started collecting information about your submission to report to my masters so they could start grading your assignment. I will report this as your submission of record:
  + Commit ID: **{}**
  + Committed on: **{}**
  + Commit Message: **{}**

> if you wish to make a late submission, please **ignore** this issue, close it and follow the [submission instructions](http://www-scf.usc.edu/~csci104/assignments/submission-instructions.html) on the course website.

> This is an issue on your GitHub repository issue tracker. Make sure you close this issue after confirming the information in it is correct.""".format(ssubmissions[s].commit_sha, convertTime(ssubmissions[s].commit_timestamp), ssubmissions[s].commit_message.encode("utf8"))
	res = gh.post('https://api.github.com/repos/{}/{}/issues'.format(ssubmissions[s].repo_org, ssubmissions[s].repo_name), issue)
	
	if res is None:
		#print ssubmissions[s].__dict__
		print '[ERROR][ISSUE] {}/{} https://github.com/{}'.format(ssubmissions[s].repo_org, ssubmissions[s].repo_name, ssubmissions[s].github_username)

