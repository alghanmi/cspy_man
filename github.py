import requests
import simplejson

class github:
	__doc__ = 'GitHub client'
	
	def __init__(self, gh_username, gh_password):
		self.username = gh_username
		self.password = gh_password

	def get(self, url):
		'''Return a dict with the result of a GET request'''
		return get(self, url, True)

	def get(self, url, pagination):
		'''Return a dict with the result of a GET request'''
		r = requests.get(url, auth=(self.username, self.password))
		if r.status_code == 200:
			res = simplejson.loads(r.content)
			if 'next' in r.links and pagination is True:
				res.extend(gitHubRequest(r.links['next']['url']))
        
			return res
		else:
			print "[ERROR] Bad Request. Status Code", r.status_code
			return None
	
	def post(self, url, payload):
		''' Send a POST request to GitHub via API '''
		r = requests.post(url, data=simplejson.dumps(payload), auth=(self.username, self.password))
		res = simplejson.loads(r.content)
		
		if r.status_code == 201:
			return res

		else:
			details = ""
			if 'errors' in res:
				for e in res['errors']:
					details += "{}.{}: {}.".format(e['resource'], e['field'], e['code'])
			print "[ERROR][HTTP {}] {} - {}".format(r.status_code, res["message"], details)
			return None

