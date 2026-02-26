from app import create_app
from app.services import AuthService, MissionService

app = create_app()
app.testing = True
app.config['PROPAGATE_EXCEPTIONS'] = True

with app.app_context():
    # ensure a test user with a mission exists
    if not AuthService.is_email_exists('admin@example.com'):
        AuthService.register_user('Admin User', 'admin@example.com', 'password', role='ADMIN')
    user = AuthService.login('admin@example.com','password')
    # if no mission exists create one
    missions = MissionService.get_all_missions()
    if not missions:
        # create a course and unit to link tasks? we'll cheat by directly
        MissionService.create_mission('Test Mission', user.id, [])
    mission_id = MissionService.get_all_missions()[0].id

with app.test_client() as c:
    c.post('/login', data={'email':'admin@example.com','password':'password'}, follow_redirects=True)
    resp = c.get(f'/missions/{mission_id}', follow_redirects=True)
    print('mission detail status', resp.status_code)
    print(resp.get_data(as_text=True)[:1000])
