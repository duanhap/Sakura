from app import create_app

app = create_app()
app.testing = True
app.config['PROPAGATE_EXCEPTIONS'] = True

with app.test_client() as c:
    resp = c.get('/dashboard')
    print('STATUS', resp.status_code)
    print(resp.get_data(as_text=True))
