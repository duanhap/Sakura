CREATE TABLE `User` (id int(10) NOT NULL AUTO_INCREMENT, name varchar(255) NOT NULL, email varchar(255) NOT NULL, password varchar(255) NOT NULL, avatar varchar(255), description varchar(255), wallpaper varchar(255), role varchar(255) NOT NULL, createdAt date NOT NULL, PRIMARY KEY (id));
CREATE TABLE Course (id int(10) NOT NULL AUTO_INCREMENT, name varchar(255) NOT NULL, image varchar(255), description varchar(255) NOT NULL, createdAt date NOT NULL, PRIMARY KEY (id));
CREATE TABLE Unit (id int(10) NOT NULL AUTO_INCREMENT, name varchar(255) NOT NULL, description varchar(255), video varchar(255), document varchar(255), createdAt date NOT NULL, Courseid int(10) NOT NULL, PRIMARY KEY (id));
CREATE TABLE Task (id int(10) NOT NULL AUTO_INCREMENT, name varchar(255) NOT NULL, isCompleted tinyint(1) NOT NULL DEFAULT 0, Missionid int(10) NOT NULL, Unitid int(10) NOT NULL, PRIMARY KEY (id));
CREATE TABLE Mission (id int(10) NOT NULL AUTO_INCREMENT, name varchar(255) NOT NULL, createdAt date NOT NULL, description varchar(255), Userid int(10) NOT NULL, PRIMARY KEY (id));
ALTER TABLE Task ADD CONSTRAINT FKTask604684 FOREIGN KEY (Missionid) REFERENCES Mission (id);
ALTER TABLE Task ADD CONSTRAINT FKTask417012 FOREIGN KEY (Unitid) REFERENCES Unit (id);
ALTER TABLE Unit ADD CONSTRAINT FKUnit196491 FOREIGN KEY (Courseid) REFERENCES Course (id);
ALTER TABLE Mission ADD CONSTRAINT FKMission590480 FOREIGN KEY (Userid) REFERENCES `User` (id);
CREATE TABLE Flashcard (
    id INT(10) NOT NULL AUTO_INCREMENT,
    term VARCHAR(255) NOT NULL,
    pronunciation VARCHAR(255),
    description VARCHAR(255),
    memoryTip VARCHAR(255),
    createdAt DATE NOT NULL,
    UnitId INT(10) NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE Flashcard
ADD CONSTRAINT FKFlashcard_Unit
FOREIGN KEY (UnitId) REFERENCES Unit(id);
CREATE TABLE FlashcardUser (
    id INT(10) NOT NULL AUTO_INCREMENT,
    FlashcardId INT(10) NOT NULL,
    UserId INT(10) NOT NULL,
    status ENUM('CHUA_THUOC','THUOC') NOT NULL DEFAULT 'CHUA_THUOC',
    PRIMARY KEY (id)
);

ALTER TABLE FlashcardUser
ADD CONSTRAINT FKFlashcardUser_Flashcard
FOREIGN KEY (FlashcardId) REFERENCES Flashcard(id);

ALTER TABLE FlashcardUser
ADD CONSTRAINT FKFlashcardUser_User
FOREIGN KEY (UserId) REFERENCES `User`(id);
CREATE TABLE Sentence (
    id INT(10) NOT NULL AUTO_INCREMENT,
    content VARCHAR(255) NOT NULL,
    meaning VARCHAR(255) NOT NULL,
    UnitId INT(10) NOT NULL,
    PRIMARY KEY (id)
);
ALTER TABLE Sentence
ADD COLUMN pronunciation VARCHAR(255) NOT NULL AFTER content;

ALTER TABLE Sentence
ADD CONSTRAINT FKSentence_Unit
FOREIGN KEY (UnitId) REFERENCES Unit(id);
CREATE TABLE ResultUnitTest (
    id INT(10) NOT NULL AUTO_INCREMENT,
    Userid INT(10) NOT NULL,
    Unitid INT(10) NOT NULL,
    completionTime INT NOT NULL,         -- thời gian hoàn thành (giây)
    correctPercentage FLOAT NOT NULL,    -- phần trăm đúng
    createdAt DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY unique_user_unit (Userid, Unitid)
);
ALTER TABLE ResultUnitTest
ADD CONSTRAINT FK_Result_User
FOREIGN KEY (Userid) REFERENCES `User`(id);

ALTER TABLE ResultUnitTest
ADD CONSTRAINT FK_Result_Unit
FOREIGN KEY (Unitid) REFERENCES Unit(id);