#!/usr/bin/env python
"""Test script to verify admin endpoints are registered correctly"""

from app import create_app

app = create_app()

print('\n✓ App initialized successfully!')
print('\n✓ Admin-related endpoints:')
print('=' * 60)

admin_routes = sorted(
    [rule for rule in app.url_map.iter_rules() if 'admin' in rule.endpoint],
    key=lambda r: r.rule
)

for rule in admin_routes:
    print(f'  {rule.rule:<40} -> {rule.endpoint}')

print('=' * 60)
print(f'\nTotal admin routes: {len(admin_routes)}')

# Check for specific routes we expect
expected_routes = [
    'admin.dashboard',
    'admin.missions',
    'admin.mission_new',
    'admin_mission.detail',
    'admin_mission.edit',
    'admin_mission.delete',
    'admin_mission.task_new',
    'admin_task.edit',
    'admin_task.delete',
]

print('\n✓ Checking for expected route endpoints:')
for endpoint in expected_routes:
    found = any(rule.endpoint == endpoint for rule in admin_routes)
    status = '✓' if found else '✗'
    print(f'  {status} {endpoint}')
