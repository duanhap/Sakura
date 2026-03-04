CREATE DATABASE IF NOT EXISTS sakura;
USE sakura;

CREATE TABLE `user` (
    id int(10) NOT NULL AUTO_INCREMENT,
    name varchar(255) NOT NULL,
    email varchar(255) NOT NULL,
    password varchar(255) NOT NULL,
    avatar varchar(255),
    description varchar(255),
    wallpaper varchar(255),
    role varchar(255) NOT NULL,
    createdAt date NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE course (
    id int(10) NOT NULL AUTO_INCREMENT,
    name varchar(255) NOT NULL,
    image varchar(255),
    description varchar(255) NOT NULL,
    createdAt date NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE unit (
    id int(10) NOT NULL AUTO_INCREMENT,
    name varchar(255) NOT NULL,
    description varchar(255),
    video varchar(255),
    document varchar(255),
    createdAt date NOT NULL,
    Courseid int(10) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE task (
    id int(10) NOT NULL AUTO_INCREMENT,
    name varchar(255) NOT NULL,
    isCompleted tinyint(1) NOT NULL DEFAULT 0,
    Missionid int(10) NOT NULL,
    Unitid int(10) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE mission (
    id int(10) NOT NULL AUTO_INCREMENT,
    name varchar(255) NOT NULL,
    createdAt date NOT NULL,
    description varchar(255),
    Userid int(10) NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE task 
ADD CONSTRAINT FKTask604684 
FOREIGN KEY (Missionid) REFERENCES mission (id);

ALTER TABLE task 
ADD CONSTRAINT FKTask417012 
FOREIGN KEY (Unitid) REFERENCES unit (id);

ALTER TABLE unit 
ADD CONSTRAINT FKUnit196491 
FOREIGN KEY (Courseid) REFERENCES course (id);

ALTER TABLE mission 
ADD CONSTRAINT FKMission590480 
FOREIGN KEY (Userid) REFERENCES `user` (id);

CREATE TABLE flashcard (
    id INT(10) NOT NULL AUTO_INCREMENT,
    term VARCHAR(255) NOT NULL,
    pronunciation VARCHAR(255),
    description VARCHAR(255),
    memoryTip VARCHAR(255),
    createdAt DATE NOT NULL,
    UnitId INT(10) NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE flashcard
ADD CONSTRAINT FKFlashcard_Unit
FOREIGN KEY (UnitId) REFERENCES unit(id);

CREATE TABLE flashcarduser (
    id INT(10) NOT NULL AUTO_INCREMENT,
    FlashcardId INT(10) NOT NULL,
    UserId INT(10) NOT NULL,
    status ENUM('CHUA_THUOC','THUOC') NOT NULL DEFAULT 'CHUA_THUOC',
    PRIMARY KEY (id)
);

ALTER TABLE flashcarduser
ADD CONSTRAINT FKFlashcardUser_Flashcard
FOREIGN KEY (FlashcardId) REFERENCES flashcard(id);

ALTER TABLE flashcarduser
ADD CONSTRAINT FKFlashcardUser_User
FOREIGN KEY (UserId) REFERENCES `user`(id);

CREATE TABLE sentence (
    id INT(10) NOT NULL AUTO_INCREMENT,
    content VARCHAR(255) NOT NULL,
    meaning VARCHAR(255) NOT NULL,
    UnitId INT(10) NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE sentence
ADD COLUMN pronunciation VARCHAR(255) NOT NULL AFTER content;

ALTER TABLE sentence
ADD CONSTRAINT FKSentence_Unit
FOREIGN KEY (UnitId) REFERENCES unit(id);

CREATE TABLE resultunittest (
    id INT(10) NOT NULL AUTO_INCREMENT,
    Userid INT(10) NOT NULL,
    Unitid INT(10) NOT NULL,
    completionTime INT NOT NULL,
    correctPercentage FLOAT NOT NULL,
    createdAt DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY unique_user_unit (Userid, Unitid)
);

ALTER TABLE resultunittest
ADD CONSTRAINT FK_Result_User
FOREIGN KEY (Userid) REFERENCES `user`(id);

ALTER TABLE resultunittest
ADD CONSTRAINT FK_Result_Unit
FOREIGN KEY (Unitid) REFERENCES unit(id);

ALTER TABLE course
ADD COLUMN languageCourse VARCHAR(255) NOT NULL AFTER name;

ALTER TABLE `user`
ADD COLUMN lastSeen DATETIME NULL,
ADD COLUMN currentActivity VARCHAR(255) NULL;
CREATE TABLE unitprogress (
    id INT(10) NOT NULL AUTO_INCREMENT,
    UserId INT(10) NOT NULL,
    UnitId INT(10) NOT NULL,
    lastFlashcardId INT(10),
    isRandom TINYINT(1) DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY unique_user_unit_progress (UserId, UnitId),
    CONSTRAINT FK_Progress_User FOREIGN KEY (UserId) REFERENCES `user`(id),
    CONSTRAINT FK_Progress_Unit FOREIGN KEY (UnitId) REFERENCES unit(id),
    CONSTRAINT FK_Progress_Flashcard FOREIGN KEY (lastFlashcardId) REFERENCES flashcard(id)
);
