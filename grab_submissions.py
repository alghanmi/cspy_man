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
import requests
from subprocess import CalledProcessError, check_output
from docopt import docopt

from github import github
from github_payload import github_payload
from github_payload import github_commit
from cspy_conf import cspy_conf
from template_parser import template_parser

import datetime
from dateutil import tz
import csv
import time

import traceback
from pprint import pprint

class submission:
	__doc__ = 'Submission details information'
	
	SUBMITTION_ONTIME = 0
	SUBMITTION_LATE = 1
	
	def __init__(self):
		self.repo_org = None
		self.repo_name = None
		self.repo_user = None
		self.repo_issue = None
		
		self.commit_sha = None
		self.commit_url = None
		self.commit_timestamp = None
		self.commit_message = None
		self.commit_committer = None
		
		self.late = False
		self.grace_period = False

def convertTime(time_string):
	utc = datetime.datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%SZ')
	utc = utc.replace(tzinfo=tz.gettz('UTC'))
	return utc.astimezone(tz.gettz('America/Los_Angeles'))

def parse_file(file_name, file_type):
	submissions = []
	with open(file_name, 'r') as repo_file:
		reader = csv.reader(repo_file)
		row_count = 0
		for row in reader:
			if len(row) == 0:
				continue;
	
			elif row[0].strip().startswith("#"):
				continue;
			else:
				row_count = row_count + 1
				try:
					ss = submission()
					if file_type == submission.SUBMITTION_ONTIME:
						ss.repo_org = row[0].strip()
						ss.repo_name = row[1].strip()
						ss.repo_user = row[2].strip()
					
					elif file_type == submission.SUBMITTION_LATE:
						ss.repo_org = row[0].strip()
						ss.repo_name = row[1].strip()
						ss.commit_sha = row[2].strip()
						ss.repo_issue = row[3].strip()
						if int(row[4].strip()) > 0:
							ss.late = True
						if int(row[5].strip()) > 0:
							ss.grace_period = True
					
					submissions.append(ss)
				except:
					print '[ERROR][ROW {}] {}'.format(row_count, row)
					#traceback.print_exc()
	return submissions


def get_latest_commit(gh, submission):
	res = gh.get('https://api.github.com/repos/{}/{}/commits'.format(submission.repo_org, submission.repo_name), False)
	submission.commit_sha = res[0]['sha']
	submission.commit_url = res[0]['html_url']
	submission.commit_timestamp = res[0]['commit']['committer']['date']
	submission.commit_message   = res[0]['commit']['message']

	if res[0]['committer'] is not None:
		submission.commit_committer = res[0]['committer']['login']
	else:
		submission.commit_committer = 'Your Git Client is Misconfigured'
	
	return submission

def get_confirmation_issue(submission, hw_title):
	tags = {}
	tags['HW_TITLE'] = args['<hw_title>']
	tags['COMMIT_ID'] = submission.commit_sha
	tags['COMMIT_TIMESTAMP'] = convertTime(submission.commit_timestamp)
	tags['COMMIT_COMMITTER'] = submission.commit_committer
	tags['COMMIT_MESSAGE'] = submission.commit_message.encode("utf8")
	tp = template_parser(conf.templates['confirm_submission_issue'], html=False)
	tp.replace(tags)
	issue = {}
	issue['title'] = tp.get_subject()
	if submission.repo_user != '<NONE>':
		issue['assignee'] = submission.repo_user
	issue['body'] = tp.get_body()
	
	return issue



def get_latesubmission_issue(submission, hw_title):
	tags = {}
	tags['HW_TITLE'] = args['<hw_title>']
	tags['COMMIT_ID'] = submission.commit_sha
	tags['COMMIT_TIMESTAMP'] = convertTime(submission.commit_timestamp)
	tags['COMMIT_MESSAGE'] = submission.commit_message.encode("utf8")
	tags['LATE_DAY'] = ''
	tags['GRACE_PREIOD'] = ''
	if submission.late is True:
		tags['LATE_DAY'] = 'Your request to use a late day has been noted. Once we confirm you did not deplete your late days, the penalty will be waived.'
	if submission.grace_period is True:
		tags['GRACE_PREIOD'] = 'Your request to use the grace period has been noted. You will receive a 50% penalty if you submitted with the grace period.'
	tp = template_parser(conf.templates['late_submission_issue'], html=False)
	tp.replace(tags)
	comment = {}
	comment['body'] = tp.get_body()
	
	return comment
	
def confirm_commit(gh, submission):
	res = gh.get('https://api.github.com/repos/{}/{}/git/commits/{}'.format(submission.repo_org, submission.repo_name, submission.commit_sha), False)
	if res is None:
		return False
	else:
		commit = github_commit(res)
		submission.commit_sha = commit.commit_id
		submission.commit_url = commit.commit_url
		submission.commit_timestamp = commit.commit_timestamp
		submission.commit_message   = commit.commit_message
	
	return True

def confirm_issue(gh, submission):
	''' This is just to confirm the issue exists. We are not creating an issue object as it is not needed yet '''
	res = gh.get('https://api.github.com/repos/{}/{}/issues/{}'.format(submission.repo_org, submission.repo_name, submission.repo_issue), False)
	if res is None:
		return False
	return True

if __name__ == '__main__':
	''' Parse Input Parameters '''
	args = docopt(__doc__, version='Grab Submissions v1.0')
	#pprint(args)
	''' Load Configuration '''
	conf = cspy_conf('cspy_man.conf.ini')

	''' Initialize Scripts '''
	current_time = datetime.datetime.now()
	filestring_time = current_time.strftime('%Y%m%d%H%M%S')
	gh = github(conf.github_username, conf.github_password)
		
	'''
	Grab and Report On Time Submissions
	'''
	if args['<file_name>'] is not None and args['<hw_title>'] is not None:
		submissions = parse_file(args['<file_name>'], submission.SUBMITTION_ONTIME)
		submodule_file = '{}_{}.submodule.log'.format(args['<file_name>'], filestring_time)
		submodule_log = open(submodule_file, 'w')
		
		#Get latest commit details and create submodule log
		for ss in submissions:
			get_latest_commit(gh, ss)
			submodule_log.write('git submodule --quiet add git@github.com:{}/{}.git; cd {}; git fetch --quiet; git checkout --quiet {}; cd ..\n'.format(ss.repo_org, ss.repo_name, ss.repo_name, ss.commit_sha))
		
		submodule_log.close()
		
		#Create a confirmation issue on GitHub
		for ss in submissions:
			#Prepare Issue
			issue = get_confirmation_issue(ss, args['<hw_title>'])
			
			#Check for dry run status before writing the issue
			if args['-n'] is False and args['--dry-run'] is False:
				res = gh.post('https://api.github.com/repos/{}/{}/issues'.format(ss.repo_org, ss.repo_name), issue)
				if res is None:
					#print ss.__dict__
					print '[ERROR][ISSUE] {}/{} https://github.com/{}'.format(ss.repo_org, ss.repo_name, ss.repo_user)
			else:
				print '[LOG][CREATE ISSUE][{}] {}/{} https://github.com/{}'.format(issue['title'], ss.repo_org, ss.repo_name, ss.repo_user)

	
	elif args['--late'] is True and args['<late_file_name>'] is not None and args['<hw_title>'] is not None:
		submissions = parse_file(args['<late_file_name>'], submission.SUBMITTION_LATE)
		latesubmission_file = '{}_{}.latesubmission.log'.format(args['<late_file_name>'], filestring_time)
		latesubmission_log = open(latesubmission_file, 'w')
		
		for ls in submissions:
			#Confirm commit is valid and get commit details
			valid_commit = confirm_commit(gh, ls)
			#Confirm issue is valid
			valid_issue = confirm_issue(gh, ls)
			
			if valid_commit and valid_issue:
				if args['-n'] is False and args['--dry-run'] is False:
					#Preparer a comment
					comment = get_latesubmission_issue(ls, args['<hw_title>'])
					res = gh.post('https://api.github.com/repos/{}/{}/issues/{}/comments'.format(ls.repo_org, ls.repo_name, ls.repo_issue), comment)
					latesubmission_log.write('cd {}; git fetch --quiet;git checkout --quiet {}; cd ..\n'.format(ls.repo_name, ls.commit_sha))
					
				else:
					print '[LOG][COMMENT ON ISSUE][{}] {}/{} {}'.format(ls.repo_issue, ls.repo_org, ls.repo_name, ls.commit_sha)
			
			else:
				if not valid_commit:
					print '[ERROR][BAD COMMIT ID] {}/{} {}'.format(ls.repo_org, ls.repo_name, ls.commit_sha)
				if not valid_issue:
					print '[ERROR][BAD ISSUE] {}/{} {}'.format(ls.repo_org, ls.repo_name, ls.repo_issue)

		latesubmission_log.close()
