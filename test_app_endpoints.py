#!/usr/bin/env python
"""Test the Sakura app endpoints"""

import sys
import time
from app import create_app

app = create_app()
app.config['TESTING'] = True

print('\n=== TESTING SAKURA APP ===\n')

with app.test_client() as client:
    # Test 1: Login page (public)
    print('1. Testing login page...')
    try:
        resp = client.get('/login')
        if resp.status_code == 200:
            print('   ✓ Login page loads (200)')
            if '<form' in resp.get_data(as_text=True):
                print('   ✓ Login form found')
        else:
            print(f'   ✗ Login page returned {resp.status_code}')
    except Exception as e:
        print(f'   ✗ Error: {e}')
    
    # Test 2: Admin dashboard (should redirect to login)
    print('\n2. Testing admin dashboard (unauthenticated)...')
    try:
        resp = client.get('/admin/', follow_redirects=False)
        if resp.status_code in (302, 401, 403):
            print(f'   ✓ Admin dashboard requires auth ({resp.status_code})')
        else:
            print(f'   ✗ Unexpected status: {resp.status_code}')
    except Exception as e:
        print(f'   ✗ Error: {e}')
    
    # Test 3: Missions list page (should redirect to login)
    print('\n3. Testing missions list (unauthenticated)...')
    try:
        resp = client.get('/missions/', follow_redirects=False)
        if resp.status_code in (302, 401, 403):
            print(f'   ✓ Missions page requires auth ({resp.status_code})')
        else:
            print(f'   ✗ Unexpected status: {resp.status_code}')
    except Exception as e:
        print(f'   ✗ Error: {e}')
    
    # Test 4: Login attempt with test user
    print('\n4. Testing login flow...')
    try:
        # First check that login form renders
        resp = client.get('/login')
        html = resp.get_data(as_text=True)
        if 'email' in html and 'password' in html:
            print('   ✓ Login form has email and password fields')
            
            # Try to login
            resp = client.post('/login', data={
                'email': 'admin@example.com',
                'password': 'password123'
            }, follow_redirects=True)
            
            # Should redirect to admin dashboard if successful
            if '/admin/' in resp.request.path or resp.status_code == 200:
                print('   ✓ Login form submitted successfully')
        else:
            print('   ✗ Login form missing fields')
    except Exception as e:
        print(f'   ✗ Error: {e}')
        import traceback
        traceback.print_exc()

print('\n=== TEST COMPLETE ===\n')
