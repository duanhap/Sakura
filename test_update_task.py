import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def main():
    import os, sys
    os.chdir(r"d:\LearnLanguage\Sakura")
    sys.path.insert(0, os.getcwd())
    
    from app import create_app
    from app.extensions import db
    from app.models import Task, Mission
    from app.repositories import TaskRepository

    app = create_app()
    with app.app_context():
        m = Mission.query.first()
        t = Task(name="test_task_sql", Missionid=m.id, isCompleted=True)
        db.session.add(t)
        db.session.commit()
        
        print("\n\n====== STARTING UPDATE ======\n")
        task = Task.query.get(t.id)
        # Check initial
        print("Initial task.isCompleted:", task.isCompleted, "type:", type(task.isCompleted))
        
        # update property
        setattr(task, "isCompleted", False)
        print("After setattr task.isCompleted:", task.isCompleted, "type:", type(task.isCompleted))
        
        # commit
        db.session.commit()
        
        # query again
        new_task = Task.query.get(t.id)
        print("After commit new_task.isCompleted:", new_task.isCompleted, "type:", type(new_task.isCompleted))
        print("\n====== FINISHED UPDATE ======\n\n")
        
        db.session.delete(t)
        db.session.commit()

if __name__ == "__main__":
    main()
