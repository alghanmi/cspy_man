from subprocess import CalledProcessError, check_output

class github_payload:
	__doc__ = 'GitHub JSON Payload Parser'
	
	def __init__(self, payload):
		#Basic Repo information
		self.repo_org = payload['repository']['owner']['name']
		self.repo_name = payload['repository']['name']
		self.repo_url = payload['repository']['url']
		
		#Commit information -- number of commits for this push
		self.commit_count = len(payload['commits'])
		self.commit_id = payload['head_commit']['id']
		self.commit_url = payload['head_commit']['url']
		self.commit_timestamp = payload['head_commit']['timestamp']
		
		#Author information -- name, email and GitHub username for author of latest/head commit
		self.author_name = payload['head_commit']['author']['name']
		self.author_email = payload['head_commit']['author']['email']
		self.author_gh_username = payload['head_commit']['author']['username']
		
		self.author_emailstring = '{} <{}>'.format(self.author_name, self.author_email)
