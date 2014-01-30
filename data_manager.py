"""
Course Data Manager - Parse and Manage Rosters and Student Information

Usage:
	data_manager.py roster <course> <semester> <db_file> <roster_file> [<roster_file> ...]
	data_manager.py github <db_file> --accounts <accounts_file>
	data_manager.py github <db_file> --teams <teams_file>
	data_manager.py github <db_file> --repos <repos_file>

Arguments:
	<db_file>		the sqlite file to store the roster
    <roster_file>	GRS roster file
    <course>		The course id that the rosters belong to
    <semester>		The semester id using
    <accounts_file>	CSV file with (usc-account, github_username) records
    <teams_file>	CSV file with (github_org, usc-account, team_id, team_name) records
    <repos_file>	CSV file with (github_org, repo-name, usc-account) records

Options:
	-h --help	This screen
	--version	Software version number
"""

import csv
from docopt import docopt
import re

import sqlite3

import traceback
from pprint import pprint

class roster_section:
	__doc__ = 'A section object with a complete roster'
	
	def __init__(self):
		self.course = None
		self.semester = None
		self.section_id = None
		self.students = None
	
	def __init__(self, course, semester, section, students):
		self.course = course
		self.semester = semester
		self.section_id = section
		self.students = students
	
	def get_sql_student_info(self):
		student_info = []
		for rs in self.students:
			student_info.append(rs.get_sql_insert())
		return student_info
	
	def get_sql_roster(self):
		roster_info = []
		for rs in self.students:
			roster_info.append((rs.usc_id, self.section_id, self.semester, rs.is_w, rs.grade_option))
		return roster_info
		
	def get_student_ids(self):
		student_ids = []
		for s in self.students:
			student_ids.append(s.usc_id)
		return student_ids

class roster_student:
	__doc__ = 'A student object as represented in a roster'
	
	def __init__(self):
		self.last_name = None
		self.first_name = None
		self.middle_name = None
		self.degree = None
		self.major = None
		self.level = None
		self.email = None
		self.usc_id = None
		self.is_w = False
		self.grade_option = None
	
	def get_sql_insert(self):
		args = (self.usc_id, self.email, self.last_name, self.first_name, self.middle_name, self.major, self.level)
		return args


def get_section_id(file_name):
	r = re.match('.*\\((.*)\\)\.\w*$', file_name)	
	section_no = r.group(1)
	
	return section_no

def parse_roster_student(csv_reader):		
	row_count = 0
	students = []
	for row in csv_reader:
		row_count = row_count + 1
		#ignore header row
		if row_count == 1:
			continue;
		#ignore an empty row
		elif len(row) == 0:
			continue;
		#ignore a row that starts with a '#', i.e. a comment
		elif row[0].strip().startswith("#"):
			continue;
		#parse the file
		else:
			try:
				s = roster_student()
				
				#split name into last, first and middle
				name = row[0].split(',')
				s.last_name = name[0].strip()
				s.first_name = name[1].strip()
				if len(name) > 2:
					s.middle_name = name[2].strip()
				
				s.degree = row[1]
				s.major = row[2]
				s.level = row[3]
				s.email = row[4]
				s.usc_id = row[5]
				
				if row[6] == 'Y':
					s.is_w = True
				s.grade_option = row[7]
				students.append(s)
			except:
				print '[ERROR][{}][ROW {}] {}'.format(rfile_name, row_count, row)
				traceback.print_exc()
	
	return students

def db_update(db, query_values, query):	
	db.executemany(query, query_values)
	db.commit()

def db_select(db, query_values, query):
	result = db.execute(query, query_values)
	return result

QUERY_INSERT_STUDENT = 'INSERT OR REPLACE INTO student(usc_id, email, last_name, first_name, middle_name, major, class) VALUES(?, ?, ?, ?, ?, ?, ?)'
QUERY_INSERT_ROSTER = 'INSERT OR REPLACE INTO roster(student_id, section_id, semester, is_w, grade_option) VALUES(?, ?, ?, ?, ?)'
QUERY_DELETE_STUDENT_FROM_ROSTER = 'DELETE FROM roster WHERE student_id = ? AND section_id = ? AND semester = ?'
QUERY_SELECT_STUDENT_IDS_IN_SECTION = 'SELECT student_id FROM roster WHERE section_id = ? AND semester = ?'

if __name__ == '__main__':
	''' Parse Input Parameters '''
	args = docopt(__doc__, version='Roster Manager v0.3')
	pprint(args)
	
	'''Parse roster files'''
	if args['roster'] is True:
		course = args['<course>']
		semester = args['<semester>']
		sections = []
		for rfile_name in args['<roster_file>']:
			''' Get individual section details '''
			section_id = get_section_id(rfile_name)
			print 'Parsing [{}] {} section {}'.format(semester, course, section_id)
			with open(rfile_name, 'r') as roster_file:
				reader = csv.reader(roster_file, delimiter='\t', quotechar='"')
				students = parse_roster_student(reader)
			
				section = roster_section(course, semester, section_id, students)
				sections.append(section)
	
		'''Update database with roster '''
		db = None
		try:
			#initiate connection
			db = sqlite3.connect(args['<db_file>'])
			db.executescript('PRAGMA foreign_keys = ON;')
			db_curser = db.cursor()
		
			'''Insert or update student information'''
			for s in sections:
				print 'Updating student information for section {}-{}'.format(s.course, s.section_id)
				db_update(db, s.get_sql_student_info(), QUERY_INSERT_STUDENT)
			
		
			'''Update Section Rosters'''
			for s in sections:
				print 'Updating student roster for section {}-{}'.format(s.course, s.section_id)
				db_update(db, s.get_sql_roster(), QUERY_INSERT_ROSTER)
			
				#Remove students who are no longer in the section
				result_set = db_select(db, (s.section_id, s.semester) , QUERY_SELECT_STUDENT_IDS_IN_SECTION)
				db_student_ids = []
				current_student_ids = s.get_student_ids()
				for si in result_set:
					db_student_ids.append(si[0].encode('ascii', 'replace'))
			
				unregistered = list(set(db_student_ids) - set(current_student_ids))
				unregistered_query_data = []
				for u in unregistered:
					print '[LOG][WARN] Removing {} from {}-{}'.format(u, s.course, s.section_id)
					unregistered_query_data.append((u, s.section_id, s.semester))
				if len(unregistered_query_data) > 0:
					db_update(db, unregistered_query_data, QUERY_DELETE_STUDENT_FROM_ROSTER)
	
		except sqlite3.Error as e:
			print '[ERROR][SQLITE3] {}'.format(e.args[0])
	
		finally:
			if db is not None:
				db.close()
				

	elif args['github'] is True:
		if args['--accounts'] is True:
			print 'parsing accounts'
		
		elif args['--teams'] is True:
			print 'parsing teams'
	
		elif args['--repos'] is True:
			print 'parsing repos'
	
	
	
