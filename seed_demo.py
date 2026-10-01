"""
Demo data seeding script - Creates 5 employees with full availability schedules and a sample meeting.
Run with: python seed_demo.py
"""
import os, sys, django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Availability
from meetings.models import Meeting, MeetingParticipant
from datetime import date, time, timedelta

User = get_user_model()

EMPLOYEES = [
    dict(username='Rahul', first_name='Rahul', last_name='Kumar', email='rahul@company.com',
         employee_id='EMP-0001', department='Engineering', job_role='Senior Manager'),
    dict(username='Priya', first_name='Priya', last_name='Sharma', email='priya@company.com',
         employee_id='EMP-0002', department='QA', job_role='QA Lead'),
    dict(username='Anil', first_name='Anil', last_name='Verma', email='anil@company.com',
         employee_id='EMP-0003', department='Product', job_role='Client Relations Lead'),
    dict(username='Sneha', first_name='Sneha', last_name='Mehta', email='sneha@company.com',
         employee_id='EMP-0004', department='Engineering', job_role='Backend Developer'),
    dict(username='Vikram', first_name='Vikram', last_name='Singh', email='vikram@company.com',
         employee_id='EMP-0005', department='Design', job_role='UI/UX Designer'),
    dict(username='Akhila', first_name='Akhila', last_name='Reddy', email='akhila.reddy@company.com',
         employee_id='EMP-0006', department='Engineering', job_role='Full Stack Developer'),
    dict(username='Bala', first_name='Bala', last_name='Krishna', email='bala.krishna@company.com',
         employee_id='EMP-0007', department='DevOps', job_role='DevOps Engineer'),
    dict(username='Kavya', first_name='Kavya', last_name='Prasad', email='kavya.prasad@company.com',
         employee_id='EMP-0008', department='QA', job_role='Test Automation Engineer'),
    dict(username='Madhu', first_name='Madhu', last_name='Babu', email='madhu.babu@company.com',
         employee_id='EMP-0009', department='Product', job_role='Product Manager'),
    dict(username='Sarasu', first_name='Sarasu', last_name='Devi', email='sarasu.devi@company.com',
         employee_id='EMP-0010', department='HR', job_role='HR Manager'),
    dict(username='Rajitha', first_name='Rajitha', last_name='Kumari', email='rajitha.kumari@company.com',
         employee_id='EMP-0011', department='Finance', job_role='Finance Analyst'),
    dict(username='Sruthi', first_name='Sruthi', last_name='Varma', email='sruthi.varma@company.com',
         employee_id='EMP-0012', department='Engineering', job_role='Backend Developer'),
    dict(username='Rama', first_name='Rama', last_name='Rao', email='rama.rao@company.com',
         employee_id='EMP-0013', department='Marketing', job_role='Marketing Lead'),
    dict(username='Kundana', first_name='Kundana', last_name='Sri', email='kundana.sri@company.com',
         employee_id='EMP-0014', department='Engineering', job_role='Frontend Developer'),
    dict(username='Pavani', first_name='Pavani', last_name='Gupta', email='pavani.gupta@company.com',
         employee_id='EMP-0015', department='Design', job_role='UI/UX Designer'),
    dict(username='Gowri', first_name='Gowri', last_name='Shankar', email='gowri.shankar@company.com',
         employee_id='EMP-0016', department='Operations', job_role='Operations Manager'),
]

created_users = []
for emp in EMPLOYEES:
    user, created = User.objects.get_or_create(
        username=emp['username'],
        defaults={**emp, 'is_staff': False}
    )
    if created:
        user.set_password('demo1234')
        user.save()
        print(f"  Created employee: {user.get_full_name()}")
    else:
        print(f"  Exists: {user.get_full_name()}")
    created_users.append(user)

# Set weekly availability for all employees (Mon-Fri 09:00-17:00)
for user in created_users:
    for day in range(5):  # Monday to Friday
        Availability.objects.get_or_create(
            user=user,
            day_of_week=day,
            defaults={'start_time': time(9, 0), 'end_time': time(17, 0), 'is_available': True}
        )

# Mark Anil as Busy to demo unavailability
anil = User.objects.get(username='Anil')
anil.status = 'Busy'
anil.save()

organizer = created_users[0]  # Rahul organizes

# Create 3 sample meetings
meeting_date = date.today() + timedelta(days=1)
if meeting_date.weekday() >= 5:
    meeting_date += timedelta(days=2)

meetings_data = [
    dict(title='Project Release & Sprint Planning', meeting_type='Project Meeting', priority='High',
         date=meeting_date, start_time=time(10, 0), end_time=time(11, 0),
         agenda='Review Q3 deliverables, Sprint 14 kickoff', status='Scheduled'),
    dict(title='API Integration Review', meeting_type='Review Meeting', priority='Medium',
         date=meeting_date, start_time=time(14, 0), end_time=time(15, 0),
         agenda='Review API contracts and testing milestones', status='Scheduled'),
    dict(title='Team Retrospective', meeting_type='Team Meeting', priority='Low',
         date=meeting_date + timedelta(days=1), start_time=time(11, 0), end_time=time(12, 0),
         agenda='Discuss what went well, blockers, improvements', status='Pending Confirmation'),
]

for m_data in meetings_data:
    meeting, created = Meeting.objects.get_or_create(
        organizer=organizer,
        title=m_data['title'],
        defaults=m_data
    )
    if created:
        print(f"  Created meeting: {meeting.title}")
    else:
        print(f"  Meeting exists: {meeting.title}")
        
    for u in created_users:
        MeetingParticipant.objects.get_or_create(
            meeting=meeting,
            user=u,
            defaults={'response_status': 'Accepted' if u == organizer else 'Pending'}
        )

print("\n[OK] Demo seed complete! All 16 team members registered and attached as participants.")
print("   Login at: http://127.0.0.1:8000/login/")
print("   Admin at:  http://127.0.0.1:8000/admin/ (admin / <set via createsuperuser>)")
print("\n   Demo Employee Logins:")
for emp in EMPLOYEES:
    print(f"   - {emp['first_name']} {emp['last_name']} ({emp['job_role']})")
