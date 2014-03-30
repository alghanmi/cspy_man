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
		self.commit_message = payload['head_commit']['message']
		
		self.commits = [ ]
		#Getting individual commit information
		for c in payload['commits']:
			gcommit = github_commit(c['id'], c['message'], c['timestamp'], c['url'], c['author']['name'], c['author']['email'], c['author']['username'])
			self.commits.append(gcommit)			
		
		#Author information -- name, email and GitHub username for author of latest/head commit
		self.author_name = payload['head_commit']['author']['name']
		self.author_email = payload['head_commit']['author']['email']
		self.author_gh_username = payload['head_commit']['author']['username']
		
		self.author_emailstring = '{} <{}>'.format(self.author_name, self.author_email)

class github_commit:
	__doc__ = 'A GitHub Commit Object'
	
	def __init__(self, commit_id, message, timestamp, url, author_name, author_email, author_gh_username):
		self.commit_id = commit_id
		self.commit_message = message
		self.commit_timestamp = timestamp
		self.commit_url = url
		self.author_name = author_name
		self.author_email = author_email
		self.author_gh_username = author_gh_username
	
	@classmethod
	def from_payload(cls, payload):
		''' Generate commit from payload '''
		commit_id = payload['sha']
		commit_message = payload['message']
		commit_timestamp = payload['author']['date']
		commit_url = payload['html_url']
		author_name = payload['author']['name']
		author_email = payload['author']['email']

		#Not part of GitHub API single commit payload
		#http://developer.github.com/v3/git/commits/#get-a-commit
		author_gh_username = None
	
		return cls(commit_id, commit_message, commit_timestamp, commit_url, author_name, author_email, author_gh_username)
