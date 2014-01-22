PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS commit_log;
DROP TABLE IF EXISTS github_account;
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
	level			CHAR,
	
	PRIMARY KEY(usc_id)
);

CREATE TABLE IF NOT EXISTS roster (
	student_id		CHAR,
	section_id		CHAR,
	semester		CHAR,
	
	is_w			INTEGER,
	grade_option	TEXT,
	
	PRIMARY KEY(student_id, section_id, semester),
	FOREIGN KEY(student_id) REFERENCES student(student_id),
	FOREIGN KEY(section_id, semester) REFERENCES section(section_id, semester)
);


CREATE TABLE IF NOT EXISTS github_account (
	student_id		CHAR,
	github_username	CHAR,
	
	PRIMARY KEY(student_id, github_username),
	FOREIGN KEY(student_id) REFERENCES student(student_id)
);

CREATE TABLE IF NOT EXISTS commit_log (
);

