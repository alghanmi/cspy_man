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
	is_project		INTEGER,
	repo_prefix		CHAR,
	
	PRIMARY KEY(course_id, semester, hw_id),
	FOREIGN KEY(course_id) REFERENCES course(course_id)
);

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

