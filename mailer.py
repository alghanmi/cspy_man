import smtplib
from cspy_conf import cspy_conf

class mailer:
	__doc__ = 'Send email through an SMTP server'
	
	def __init__(self, conf):
		self.conf = conf
		

	def create_header(self, subject, to):
		headers = []
		headers.append('From: ' + self.conf.email_from)
		headers.append('Subject: ' + subject)
		headers.append('to: ' + to)
		if self.conf.email_replyto is not None:
			headers.append('reply-to: ' + self.conf.email_replyto)
		headers.append('MIME-Version: 1.0')
		headers.append('Content-Type: text/html')
		
		self.header = "\r\n".join(headers)
	
	def session_start(self):
		self.session = smtplib.SMTP(self.conf.email_server, self.conf.email_port)
		#self.session.set_debuglevel(True)
		self.session.ehlo()
		self.session.starttls()
		self.session.ehlo
		self.session.login(self.conf.email_username, self.conf.email_password)
	
	def session_end(self):
		self.session.quit()
	
	def send(self, subject, to, body):
		self.create_header(subject, to)
		self.session_start()
		self.session.sendmail(self.conf.email_from, to, self.header + "\r\n\r\n" + body)
		self.session_end()
