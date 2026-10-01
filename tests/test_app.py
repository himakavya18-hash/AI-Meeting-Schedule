from datetime import date, time, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import Availability
from meetings.models import Meeting, MeetingParticipant
from meetings.services import check_participants_availability, suggest_alternative_time_slots
from transcripts.models import MeetingTranscript
from transcripts.parsers import parse_txt
from ai_extractor.schemas import validate_extraction_schema
from ai_extractor.extractor import run_heuristic_mock_extraction, analyze_transcript_with_ai
from ai_extractor.services import process_transcript_and_save_analysis
from actions.models import Decision, ActionItem, UnresolvedQuestion, Dependency

User = get_user_model()

class MeetingPortalSystemTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create 4 test employees
        self.user_rahul = User.objects.create_user(
            username='rahul', email='rahul@company.com', password='pass123',
            first_name='Rahul', employee_id='EMP-0001', department='Engineering', job_role='Manager'
        )
        self.user_priya = User.objects.create_user(
            username='priya', email='priya@company.com', password='pass123',
            first_name='Priya', employee_id='EMP-0002', department='QA', job_role='QA Lead'
        )
        self.user_anil = User.objects.create_user(
            username='anil', email='anil@company.com', password='pass123',
            first_name='Anil', employee_id='EMP-0003', department='Product', job_role='Client Lead'
        )
        self.user_sneha = User.objects.create_user(
            username='sneha', email='sneha@company.com', password='pass123',
            first_name='Sneha', employee_id='EMP-0004', department='Engineering', job_role='Dev'
        )

        # Set up weekly availability
        for u in [self.user_rahul, self.user_priya, self.user_anil, self.user_sneha]:
            for d in range(5):
                Availability.objects.create(user=u, day_of_week=d, start_time='09:00:00', end_time='17:00:00', is_available=True)

        self.meeting_date = date.today() + timedelta(days=1)
        # Force meeting date to a weekday
        if self.meeting_date.weekday() >= 5:
            self.meeting_date += timedelta(days=2)

    # Test 1: User Login
    def test_01_demo_login(self):
        response = self.client.post('/api/accounts/demo-login/', {'username': 'rahul'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)

    # Test 2: Unauthorized Access Protection
    def test_02_unauthorized_access(self):
        response = self.client.get('/api/meetings/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


    # Test 3: Meeting Creation
    def test_03_create_meeting(self):
        self.client.force_authenticate(user=self.user_rahul)
        payload = {
            'title': 'Project Review & Sprint Launch',
            'meeting_type': 'Review Meeting',
            'priority': 'High',
            'date': str(self.meeting_date),
            'start_time': '10:00:00',
            'end_time': '11:00:00',
            'agenda': 'Review quarterly roadmap',
            'participant_ids': [self.user_priya.id, self.user_anil.id, self.user_sneha.id]
        }
        response = self.client.post('/api/meetings/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Meeting.objects.count(), 1)

    # Test 4: Participant Selection Count
    def test_04_participant_selection(self):
        self.client.force_authenticate(user=self.user_rahul)
        meeting = Meeting.objects.create(
            title='Team Sync', organizer=self.user_rahul, date=self.meeting_date,
            start_time=time(10, 0), end_time=time(11, 0)
        )
        MeetingParticipant.objects.create(meeting=meeting, user=self.user_rahul, response_status='Accepted')
        MeetingParticipant.objects.create(meeting=meeting, user=self.user_priya, response_status='Pending')
        self.assertEqual(meeting.participants.count(), 2)

    # Test 5: All Participants Available Check
    def test_05_all_participants_available(self):
        users = [self.user_rahul, self.user_priya, self.user_sneha]
        avail_res = check_participants_availability(users, self.meeting_date, time(10, 0), time(11, 0))
        self.assertTrue(avail_res['all_available'])
        self.assertEqual(avail_res['available_count'], 3)

    # Test 6: Some Participants Unavailable Check
    def test_06_some_participants_unavailable(self):
        # Mark Anil as On Leave
        self.user_anil.status = 'On Leave'
        self.user_anil.save()

        users = [self.user_rahul, self.user_priya, self.user_anil]
        avail_res = check_participants_availability(users, self.meeting_date, time(10, 0), time(11, 0))
        self.assertFalse(avail_res['all_available'])
        self.assertEqual(avail_res['unavailable_count'], 1)

    # Test 7: Alternative Time Suggestion Engine
    def test_07_alternative_time_suggestion(self):
        # Create a conflicting meeting for Priya at 10:00-11:00
        m_conflict = Meeting.objects.create(
            title='QA Training', organizer=self.user_priya, date=self.meeting_date,
            start_time=time(10, 0), end_time=time(11, 0)
        )
        MeetingParticipant.objects.create(meeting=m_conflict, user=self.user_priya, response_status='Accepted')

        users = [self.user_rahul, self.user_priya, self.user_sneha]
        suggestions = suggest_alternative_time_slots(users, self.meeting_date, time(10, 0), time(11, 0))
        self.assertGreater(len(suggestions), 0)
        # Top suggested slot should have max participants available
        self.assertEqual(suggestions[0]['available_count'], 3)

    # Test 8: Email Notification Service Call
    def test_08_email_notification(self):
        from notifications.email_service import send_meeting_invitation_email
        meeting = Meeting.objects.create(
            title='Architecture Alignment', organizer=self.user_rahul, date=self.meeting_date,
            start_time=time(14, 0), end_time=time(15, 0)
        )
        send_meeting_invitation_email(meeting, self.user_priya)
        # Should execute without errors

    # Test 9: Meeting Acceptance
    def test_09_meeting_acceptance(self):
        meeting = Meeting.objects.create(
            title='Design Review', organizer=self.user_rahul, date=self.meeting_date,
            start_time=time(11, 0), end_time=time(12, 0)
        )
        part = MeetingParticipant.objects.create(meeting=meeting, user=self.user_priya, response_status='Pending')
        
        self.client.force_authenticate(user=self.user_priya)
        res = self.client.post(f'/api/meetings/{meeting.id}/respond/', {'response_status': 'Accepted'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        part.refresh_from_db()
        self.assertEqual(part.response_status, 'Accepted')

    # Test 10: Meeting Rejection
    def test_10_meeting_rejection(self):
        meeting = Meeting.objects.create(
            title='Optional Sync', organizer=self.user_rahul, date=self.meeting_date,
            start_time=time(16, 0), end_time=time(17, 0)
        )
        part = MeetingParticipant.objects.create(meeting=meeting, user=self.user_anil, response_status='Pending')
        self.client.force_authenticate(user=self.user_anil)
        res = self.client.post(f'/api/meetings/{meeting.id}/respond/', {'response_status': 'Declined'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # Test 11: Transcript Upload & TXT Parser
    def test_11_transcript_upload(self):
        meeting = Meeting.objects.create(
            title='Quarterly Planning', organizer=self.user_rahul, date=self.meeting_date,
            start_time=time(10, 0), end_time=time(11, 0)
        )
        MeetingParticipant.objects.create(meeting=meeting, user=self.user_rahul, response_status='Accepted')

        self.client.force_authenticate(user=self.user_rahul)
        raw_text = "Rahul: We should deploy the new application version by Friday.\nPriya: I will complete the API testing by Thursday."
        res = self.client.post('/api/transcripts/upload/', {
            'meeting_id': meeting.id,
            'raw_text': raw_text
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MeetingTranscript.objects.count(), 1)

    # Test 12: AI Extraction Service
    def test_12_ai_extraction(self):
        text = "Rahul: We should deploy the new version by Friday.\nPriya: I will complete the API testing by Thursday."
        extracted = analyze_transcript_with_ai(text)
        is_valid, cleaned = validate_extraction_schema(extracted)
        self.assertTrue(is_valid)
        self.assertIn("meeting_summary", cleaned)

    # Test 13: Decision Extraction
    def test_13_decision_extraction(self):
        text = "Manager: Manager confirmed that the release will happen on Friday."
        extracted = analyze_transcript_with_ai(text)
        self.assertGreater(len(extracted['decisions']), 0)

    # Test 14: Action Extraction
    def test_14_action_extraction(self):
        text = "Priya: I will complete the API testing by Thursday."
        extracted = analyze_transcript_with_ai(text)
        self.assertGreater(len(extracted['action_items']), 0)

    # Test 15: Owner Extraction & Mapping
    def test_15_owner_extraction_and_mapping(self):
        meeting = Meeting.objects.create(
            title='Sprint Kickoff', organizer=self.user_rahul, date=self.meeting_date,
            start_time=time(10, 0), end_time=time(11, 0)
        )
        MeetingParticipant.objects.create(meeting=meeting, user=self.user_rahul, response_status='Accepted')

        transcript = MeetingTranscript.objects.create(
            meeting=meeting,
            raw_text="Priya: I will complete the API testing by Thursday.",
            uploaded_by=self.user_rahul
        )
        res = process_transcript_and_save_analysis(transcript)
        actions = ActionItem.objects.filter(meeting=meeting)
        self.assertGreater(actions.count(), 0)
        # Should map owner to user_priya
        priya_action = actions.filter(owner_user=self.user_priya).first()
        self.assertIsNotNone(priya_action)

    # Test 16: Deadline Extraction
    def test_16_deadline_extraction(self):
        text = "Rahul: Deployment will be completed by Friday."
        extracted = analyze_transcript_with_ai(text)
        self.assertTrue(any("Friday" in a.get('deadline', '') or "Friday" in a.get('task', '') for a in extracted['action_items']))

    # Test 17: Unresolved Question Extraction
    def test_17_unresolved_question_extraction(self):
        text = "Anil: Who will provide final client approval?"
        extracted = analyze_transcript_with_ai(text)
        self.assertGreater(len(extracted['unresolved_questions']), 0)

    # Test 18: Dependency Extraction
    def test_18_dependency_extraction(self):
        text = "Rahul: Deployment strictly depends on successful API testing by Priya."
        extracted = analyze_transcript_with_ai(text)
        self.assertGreater(len(extracted['dependencies']), 0)

    # Test 19: Hallucination Prevention & Evidence Grounding Check
    def test_19_hallucination_prevention_evidence(self):
        text = "Priya: I will complete the API testing by Thursday."
        extracted = analyze_transcript_with_ai(text)
        for action in extracted['action_items']:
            self.assertTrue('evidence' in action)
            self.assertNotEqual(action['evidence'], "")

    # Test 20: Action Status Update & Overdue Check
    def test_20_action_status_update(self):
        meeting = Meeting.objects.create(
            title='Task Review', organizer=self.user_rahul, date=self.meeting_date,
            start_time=time(10, 0), end_time=time(11, 0)
        )
        action = ActionItem.objects.create(
            meeting=meeting, task='Complete API testing', owner_name='Priya',
            owner_user=self.user_priya, deadline='Thursday', status='Pending'
        )
        self.client.force_authenticate(user=self.user_priya)
        res = self.client.put(f'/api/actions/{action.id}/', {'status': 'Completed'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        action.refresh_from_db()
        self.assertEqual(action.status, 'Completed')

    # Test 21: User Registration with Email and Password
    def test_21_user_registration(self):
        reg_data = {
            'first_name': 'NewUser',
            'last_name': 'Test',
            'email': 'newuser@company.com',
            'password': 'strongpassword123',
            'department': 'Engineering',
            'job_role': 'Full Stack Developer'
        }
        res = self.client.post('/api/accounts/register/', reg_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', res.data)
        self.assertEqual(res.data['user']['email'], 'newuser@company.com')

        # Verify password is encrypted and can authenticate
        new_user = User.objects.get(email='newuser@company.com')
        self.assertTrue(new_user.check_password('strongpassword123'))
        # Verify default 5-day availability was created
        self.assertEqual(Availability.objects.filter(user=new_user).count(), 5)

    # Test 22: Email & Password Login
    def test_22_email_password_login(self):
        # Successful login by email
        res = self.client.post('/api/accounts/login/', {
            'email': 'rahul@company.com',
            'password': 'pass123'
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['user']['username'], 'rahul')

        # Successful login by username
        res2 = self.client.post('/api/accounts/login/', {
            'email': 'rahul',
            'password': 'pass123'
        })
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

        # Rejected with wrong password
        res3 = self.client.post('/api/accounts/login/', {
            'email': 'rahul@company.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(res3.status_code, status.HTTP_400_BAD_REQUEST)

    # Test 23: Custom Participant Selection in Meeting
    def test_23_custom_participant_selection(self):
        self.client.force_authenticate(user=self.user_rahul)
        # Choose only Priya and Sneha (exclude Anil)
        selected_ids = [self.user_priya.id, self.user_sneha.id]
        payload = {
            'title': 'Frontend & Backend Sync',
            'meeting_type': 'Project Meeting',
            'priority': 'Medium',
            'date': str(self.meeting_date),
            'start_time': '14:00:00',
            'end_time': '15:00:00',
            'agenda': 'Sync on REST endpoints',
            'participant_ids': selected_ids
        }
        res = self.client.post('/api/meetings/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        meeting = Meeting.objects.get(id=res.data['meeting']['id'])
        participant_user_ids = list(meeting.meeting_participants.values_list('user_id', flat=True))
        # Organizer (Rahul) + Priya + Sneha = 3 total, Anil NOT included
        self.assertIn(self.user_rahul.id, participant_user_ids)
        self.assertIn(self.user_priya.id, participant_user_ids)
        self.assertIn(self.user_sneha.id, participant_user_ids)
        self.assertNotIn(self.user_anil.id, participant_user_ids)

