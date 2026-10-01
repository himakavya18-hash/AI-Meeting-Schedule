"""
Add extra employees to the portal.
Run with: .\venv\Scripts\python add_employees.py
"""
import os, sys, django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Availability
from datetime import time

User = get_user_model()

EMPLOYEES = [
    dict(username='Akhila',  first_name='Akhila',  last_name='Reddy',    email='akhila.reddy@company.com',      employee_id='EMP-0006', department='Engineering',   job_role='Full Stack Developer'),
    dict(username='Bala',    first_name='Bala',    last_name='Krishna',  email='bala.krishna@company.com',      employee_id='EMP-0007', department='DevOps',        job_role='DevOps Engineer'),
    dict(username='Kavya',   first_name='Kavya',   last_name='Prasad',   email='kavya.prasad@company.com',      employee_id='EMP-0008', department='QA',            job_role='Test Automation Engineer'),
    dict(username='Madhu',   first_name='Madhu',   last_name='Babu',     email='madhu.babu@company.com',        employee_id='EMP-0009', department='Product',       job_role='Product Manager'),
    dict(username='Sarasu',  first_name='Sarasu',  last_name='Devi',     email='sarasu.devi@company.com',       employee_id='EMP-0010', department='HR',            job_role='HR Manager'),
    dict(username='Rajitha', first_name='Rajitha', last_name='Kumari',   email='rajitha.kumari@company.com',   employee_id='EMP-0011', department='Finance',       job_role='Finance Analyst'),
    dict(username='Sruthi',  first_name='Sruthi',  last_name='Varma',    email='sruthi.varma@company.com',     employee_id='EMP-0012', department='Engineering',   job_role='Backend Developer'),
    dict(username='Rama',    first_name='Rama',    last_name='Rao',      email='rama.rao@company.com',         employee_id='EMP-0013', department='Marketing',     job_role='Marketing Lead'),
    dict(username='Kundana', first_name='Kundana', last_name='Sri',      email='kundana.sri@company.com',      employee_id='EMP-0014', department='Engineering',   job_role='Frontend Developer'),
    dict(username='Pavani',  first_name='Pavani',  last_name='Gupta',    email='pavani.gupta@company.com',     employee_id='EMP-0015', department='Design',        job_role='UI/UX Designer'),
    dict(username='Gowri',   first_name='Gowri',   last_name='Shankar',  email='gowri.shankar@company.com',    employee_id='EMP-0016', department='Operations',    job_role='Operations Manager'),
]

print("Adding employees...\n")
created_users = []

for emp in EMPLOYEES:
    user, created = User.objects.get_or_create(
        username=emp['username'],
        defaults={**emp}
    )
    if created:
        user.set_password('demo1234')
        user.save()
        print(f"  [CREATED] {user.first_name} {user.last_name} | {user.job_role} | {user.department} | {user.email}")
    else:
        print(f"  [EXISTS]  {user.first_name} {user.last_name}")
    created_users.append(user)

    # Set Mon-Fri 9am-5pm availability
    for day in range(5):
        Availability.objects.get_or_create(
            user=user,
            day_of_week=day,
            defaults={'start_time': time(9, 0), 'end_time': time(17, 0), 'is_available': True}
        )

print(f"\nDone! {len(created_users)} employees processed.")
print(f"Total employees now: {User.objects.count()}")
print("\nAll can log in at http://127.0.0.1:8000/login/ using the demo login button.")
