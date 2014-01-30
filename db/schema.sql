PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS commit_log;
DROP TABLE IF EXISTS hw_repo_log;
DROP TABLE IF EXISTS student_repository;
DROP TABLE IF EXISTS github_team;
DROP TABLE IF EXISTS github_account;
DROP TABLE IF EXISTS homework;
DROP TABLE IF EXISTS roster;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS section;
DROP TABLE IF EXISTS course;



CREATE TABLE IF NOT EXISTS course (
	course_id		CHAR,
	name			VARCHAR,
	description		TEXT,
	units			INTEGER,
	
	PRIMARY KEY(course_id)
);

INSERT INTO course VALUES('CSCI 104', 'Data Structures and Object Oriented Design', 'Introduces the student to standard data structures (linear structures such as linked lists, (balanced) trees, priority queues, and hashtables), using the C++ programming language.Prerequisite: CSCI 103 and CSCI 109. Corequisite: CSCI 170.', 4);

CREATE TABLE IF NOT EXISTS section (
	course_id		CHAR,
	section_id		CHAR,
	semester		CHAR,
	
	days			VARCHAR,
	time_start		CHAR,
	time_stop		CHAR,
	building		CHAR,
	room			CHAR,
	
	is_lec			INTEGER,
	is_lab			INTEGER,
	
	PRIMARY KEY(section_id, semester),
	FOREIGN KEY(course_id) REFERENCES course(course_id)
);

INSERT INTO section VALUES('CSCI 104', '29907', '20141', 'Tue,Thu', '09:30am', '10:50am', 'SOS', 'B46', 1, 0);
INSERT INTO section VALUES('CSCI 104', '29905', '20141', 'Tue,Thu', '11:00am', '12:20pm', 'ZHS', '352', 1, 0);
INSERT INTO section VALUES('CSCI 104', '30397', '20141', 'Tue,Thu', '12:30pm', '01:50pm', 'ZHS', '352', 1, 0);
INSERT INTO section VALUES('CSCI 104', '30294', '20141', 'Tue', '03:00pm', '04:50pm', 'WPH', 'B36', 0, 1);
INSERT INTO section VALUES('CSCI 104', '30200', '20141', 'Tue', '03:30pm', '05:20pm', 'SAL', '126', 0, 1);
INSERT INTO section VALUES('CSCI 104', '30238', '20141', 'Tue', '05:30pm', '07:20pm', 'SAL', '126', 0, 1);
INSERT INTO section VALUES('CSCI 104', '29915', '20141', 'Wed', '12:00pm', '01:50pm', 'SAL', '126', 0, 1);
INSERT INTO section VALUES('CSCI 104', '30394', '20141', 'Wed', '02:00pm', '03:50pm', 'SAL', '109', 0, 1);
INSERT INTO section VALUES('CSCI 104', '29914', '20141', 'Wed', '03:00pm', '04:50pm', 'SAL', '126', 0, 1);
INSERT INTO section VALUES('CSCI 104', '29912', '20141', 'Wed', '05:00pm', '06:50pm', 'SAL', '109', 0, 1);
INSERT INTO section VALUES('CSCI 104', '30379', '20141', 'Thu', '05:00pm', '06:50pm', 'SAL', '127', 0, 1);

CREATE TABLE IF NOT EXISTS student (
	usc_id			CHAR,
	email			VARCHAR,
	
	last_name		VARCHAR,
	first_name		VARCHAR,
	middle_name		VARCHAR,
	
	major			CHAR,
	class			CHAR,
	
	PRIMARY KEY(usc_id)
);

CREATE TABLE IF NOT EXISTS roster (
	student_id		CHAR,
	section_id		CHAR,
	semester		CHAR,
	
	is_w			INTEGER,
	grade_option	TEXT,
	
	PRIMARY KEY(student_id, section_id, semester),
	FOREIGN KEY(student_id) REFERENCES student(usc_id),
	FOREIGN KEY(section_id, semester) REFERENCES section(section_id, semester)
);

CREATE TABLE IF NOT EXISTS homework (
	course_id		CHAR,
	semester		CHAR,
	hw_id			CHAR,
	hw_name			CHAR,
	title			VARCHAR,
	deadline		CHAR,
	
	PRIMARY KEY(course_id, semester, hw_id),
	FOREIGN KEY(course_id) REFERENCES course(course_id)
);

INSERT INTO homework VALUES('CSCI 104', '20141', 'HW01', 'HW01', 'Course Overview and Review', '2014-01-22T11:59:59-08:00');
INSERT INTO homework VALUES('CSCI 104', '20141', 'HW02', 'HW02', 'Recursion and Linked Lists', '2014-01-31T11:59:59-08:00');

CREATE TABLE IF NOT EXISTS github_account (
	student_id		CHAR,
	github_username	CHAR,
	
	PRIMARY KEY(student_id, github_username),
	FOREIGN KEY(student_id) REFERENCES student(usc_id)
);

CREATE TABLE IF NOT EXISTS github_team (
	student_id		CHAR,
	repo_org		CHAR,
	org_team_id		CHAR,
	org_team_name	CHAR,
	
	PRIMARY KEY(student_id, org_team_id),
	FOREIGN KEY(student_id) REFERENCES student(usc_id)
);

CREATE TABLE IF NOT EXISTS student_repository (
	student_id		CHAR,
	repo_org		CHAR,
	repo_name		CHAR,
	repo_clone_url	CHAR,
	repo_html_url	CHAR,
	
	PRIMARY KEY(student_id, repo_org, repo_name),
	FOREIGN KEY(student_id) REFERENCES student(usc_id)
);

CREATE TABLE IF NOT EXISTS hw_repo_log (
	course_id		CHAR,
	semester		CHAR,
	hw_id			CHAR,
	
	student_id		CHAR,
	
	repo_org		CHAR,
	repo_name		CHAR,
	
	commit_id		CHAR,
	
	--not referencing roster because some students may drop the course (before W) but still have repos.
	--not referencing section because students may move sections (before W)
	PRIMARY KEY(course_id, semester, hw_id, student_id, repo_org, repo_name),
	FOREIGN KEY(student_id) REFERENCES student(usc_id),
	FOREIGN KEY(course_id, semester, hw_id) REFERENCES homework(course_id, semester, hw_id),
	FOREIGN KEY(student_id, repo_org, repo_name) REFERENCES student_repository (student_id, repo_org, repo_name)
);

CREATE TABLE IF NOT EXISTS commit_log (
	--not worrying about referential integrity because we want it to be as open as possible
	repo_org			CHAR,
	repo_name			CHAR,
	repo_url			CHAR,
	
	commit_id			CHAR,
	commit_url			CHAR,
	commit_timestamp	CHAR,
	commit_message		TEXT,
	
	author_name			CHAR,
	author_email		CHAR,
	author_github_user	CHAR,
	
	receive_timestamp	CHAR,
	
	PRIMARY KEY(repo_org, repo_name, commit_id)
);

