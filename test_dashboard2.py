from app import create_app
from app.services import AuthService

app = create_app()
app.testing = True
app.config['PROPAGATE_EXCEPTIONS'] = True

with app.app_context():
    # ensure a test user exists
    if not AuthService.is_email_exists('admin@example.com'):
        AuthService.register_user('Admin User', 'admin@example.com', 'password', role='ADMIN')

with app.test_client() as c:
    # login
    resp = c.post('/login', data={'email':'admin@example.com','password':'password'}, follow_redirects=True)
    print('login status', resp.status_code)
    # visit dashboard
    resp = c.get('/dashboard', follow_redirects=True)
    print('dashboard status', resp.status_code)
    print(resp.get_data(as_text=True)[:2000])
