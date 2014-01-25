class template_parser:
	__doc__ = 'Parse templates and replace tags'
	PREFIX_SUBJECT = '#SUBJECT:'
	PREFIX_COMMENT = '#'
	
	def __init__(self, template_file, html=True):
		#Initalize subject and body
		self.subject = 'No Subject Specified'
		self.body = 'No Body Specified'
		
		#Read template
		with open(template_file, 'r') as file:
			text = file.readlines()
		file.close
		
		#Get Subject and Body while discarding comments
		body_text = []
		for t in text:
			if t.startswith(template_parser.PREFIX_SUBJECT):
				self.subject = t.lstrip(template_parser.PREFIX_SUBJECT)
			elif t.startswith(template_parser.PREFIX_COMMENT):
				continue
			else:
				if html is True:
					line = t.replace('\n', '<br/>')
					line = line.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
				else:
					line = t
				body_text.append(line)
			self.body = ''.join(body_text)
	
	def replace(self, tags):
		''' Replace tags with values '''
		for t in tags:
			self.body = self.body.replace('${}$'.format(t), '{}'.format(tags[t]))
			self.subject = self.subject.replace('${}$'.format(t), '{}'.format(tags[t]))
	
	
	def get_subject(self):
		return self.subject.strip()
	
	def get_body(self):
		return self.body.strip()
