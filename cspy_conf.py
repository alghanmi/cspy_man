import ConfigParser
from ConfigParser import SafeConfigParser

class cspy_conf:
	__doc__ = 'c(s, py | man) configuration & properties'
	
	def __init__(self, conf_file):
		conf_parser = SafeConfigParser()
		conf_parser.read(conf_file)
		
		#STMP Email variables
		self.email_server = self.parse_option(conf_parser, 'email', 'server')
		self.email_port = self.parse_option(conf_parser, 'email', 'port')
		self.email_username = self.parse_option(conf_parser, 'email', 'username')
		self.email_password = self.parse_option(conf_parser, 'email', 'password')
		self.email_from_email = self.parse_option(conf_parser, 'email', 'from_email')
		self.email_from_name = self.parse_option(conf_parser, 'email', 'from_name')
		self.email_tls = self.parse_option(conf_parser, 'email', 'tls')
		self.email_replyto = self.parse_option(conf_parser, 'email', 'reply-to')
		self.mandrill_api = self.parse_option(conf_parser, 'email', 'mandrill_api')
		
		#GitHub Details
		self.github_username = self.parse_option(conf_parser, 'github', 'username')
		self.github_password = self.parse_option(conf_parser, 'github', 'password')
		
		#Email templates
		self.templates = self.list_to_dict(self.parse_section(conf_parser, 'email templates'))

		#External scripts to run
		self.scripts = self.list_to_dict(self.parse_section(conf_parser, 'external_scripts'))

	
	def list_to_dict(self, mylist):
		''' Convert a list of pairs to a proper dict '''
		mydict = {}
		for l in mylist:
			mydict[l[0]] = l[1]
		return mydict
	
	def parse_section(self, parser, section):
		'''Return a dictionary of all configuration parameters in a section'''
		try:
			options = parser.items(section)
			return options
		except ConfigParser.NoSectionError:
			return None
	
	def parse_option(self, parser, section, option):
		'''Return the value of a specific option in the configuration file'''
		try:
			value = parser.get(section, option)
			return value
		except ConfigParser.NoOptionError:
			return None

