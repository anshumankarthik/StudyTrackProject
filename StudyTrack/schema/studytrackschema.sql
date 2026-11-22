
CREATE DATABASE IF NOT EXISTS StudyTrack;
USE StudyTrack;

CREATE TABLE IF NOT EXISTS Homework (
    homework_id INT AUTO_INCREMENT PRIMARY KEY,
    serial_no INT NOT NULL,
    category VARCHAR(30) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    task TEXT NOT NULL,
    due_date VARCHAR(30),
    status VARCHAR(30) DEFAULT 'Pending',
    UNIQUE (category, serial_no)
);

CREATE TABLE IF NOT EXISTS Students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    class_name VARCHAR(30),
    roll_number VARCHAR(30),
    school VARCHAR(150)
);

CREATE TABLE IF NOT EXISTS StudySchedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(100) NOT NULL,
    topic TEXT NOT NULL,
    study_date VARCHAR(30),
    start_time VARCHAR(30),
    duration VARCHAR(30)
);

INSERT INTO Students (student_id, name, class_name, roll_number, school)
VALUES (1, '', '12', '', '')
ON DUPLICATE KEY UPDATE student_id = student_id;
