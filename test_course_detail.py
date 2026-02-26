from app import create_app
from app.services import AuthService, CourseService

app = create_app()
app.testing = True
app.config['PROPAGATE_EXCEPTIONS'] = True

with app.app_context():
    # ensure a test admin user exists
    if not AuthService.is_email_exists('admin@example.com'):
        AuthService.register_user('Admin User', 'admin@example.com', 'password', role='ADMIN')
    # ensure at least one course exists
    courses = CourseService.get_all_courses()
    if not courses:
        CourseService.create_course('Test Course', 'Desc')
    course_id = CourseService.get_all_courses()[0].id

with app.test_client() as c:
    c.post('/login', data={'email':'admin@example.com','password':'password'}, follow_redirects=True)
    resp = c.get(f'/courses/{course_id}', follow_redirects=True)
    print('course detail status', resp.status_code)
    print(resp.get_data(as_text=True)[:1000])
