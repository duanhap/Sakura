import os, sys

def main():
    os.chdir(r"d:\LearnLanguage\Sakura")
    sys.path.insert(0, os.getcwd())
    
    from app import create_app
    from app.extensions import db
    from sqlalchemy import text
    
    app = create_app()
    with app.app_context():
        # Execute the new SQL DDL statements for Flashcard, FlashcardUser, Sentence
        queries = [
            """
            CREATE TABLE IF NOT EXISTS Flashcard (
                id INT(10) NOT NULL AUTO_INCREMENT,
                term VARCHAR(255) NOT NULL,
                pronunciation VARCHAR(255),
                description VARCHAR(255),
                memoryTip VARCHAR(255),
                createdAt DATE NOT NULL,
                UnitId INT(10) NOT NULL,
                PRIMARY KEY (id)
            );
            """,
            """
            ALTER TABLE Flashcard
            ADD CONSTRAINT FKFlashcard_Unit
            FOREIGN KEY (UnitId) REFERENCES Unit(id);
            """,
            """
            CREATE TABLE IF NOT EXISTS FlashcardUser (
                id INT(10) NOT NULL AUTO_INCREMENT,
                FlashcardId INT(10) NOT NULL,
                UserId INT(10) NOT NULL,
                status ENUM('CHUA_THUOC','THUOC') NOT NULL DEFAULT 'CHUA_THUOC',
                PRIMARY KEY (id)
            );
            """,
            """
            ALTER TABLE FlashcardUser
            ADD CONSTRAINT FKFlashcardUser_Flashcard
            FOREIGN KEY (FlashcardId) REFERENCES Flashcard(id);
            """,
            """
            ALTER TABLE FlashcardUser
            ADD CONSTRAINT FKFlashcardUser_User
            FOREIGN KEY (UserId) REFERENCES `User`(id);
            """,
            """
            CREATE TABLE IF NOT EXISTS Sentence (
                id INT(10) NOT NULL AUTO_INCREMENT,
                content VARCHAR(255) NOT NULL,
                meaning VARCHAR(255) NOT NULL,
                UnitId INT(10) NOT NULL,
                PRIMARY KEY (id)
            );
            """,
            """
            ALTER TABLE Sentence
            ADD CONSTRAINT FKSentence_Unit
            FOREIGN KEY (UnitId) REFERENCES Unit(id);
            """
        ]
        
        for idx, query in enumerate(queries):
            try:
                db.session.execute(text(query))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error on query {idx}: {e}")
        
        print("Queries completed.")

if __name__ == "__main__":
    main()
