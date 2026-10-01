import logging
from django.contrib.auth import get_user_model
from ai_extractor.extractor import analyze_transcript_with_ai
from actions.models import Decision, ActionItem, UnresolvedQuestion, Dependency
from notifications.services import notify_action_assigned

User = get_user_model()
logger = logging.getLogger(__name__)

def process_transcript_and_save_analysis(transcript):
    """
    Runs GenAI extraction on a MeetingTranscript object and creates database entries in the Action Register.
    """
    meeting = transcript.meeting
    extracted_data = analyze_transcript_with_ai(transcript.raw_text)

    # 1. Clear previous extracted items for this meeting if re-running
    Decision.objects.filter(meeting=meeting).delete()
    ActionItem.objects.filter(meeting=meeting).delete()
    UnresolvedQuestion.objects.filter(meeting=meeting).delete()
    Dependency.objects.filter(meeting=meeting).delete()

    # 2. Save Decisions
    saved_decisions = []
    for d in extracted_data.get('decisions', []):
        obj = Decision.objects.create(
            meeting=meeting,
            decision=d['decision'],
            evidence=d.get('evidence', 'Not specified in transcript.'),
            confidence=d.get('confidence', 0.95)
        )
        saved_decisions.append(obj)

    # 3. Save Action Items and match owner
    saved_actions = []
    all_users = list(User.objects.all())
    
    for a in extracted_data.get('action_items', []):
        owner_str = a.get('owner', 'Not specified')
        assigned_user = None
        
        if owner_str and owner_str != 'Not specified':
            for u in all_users:
                full_name = u.get_full_name().lower()
                first_name = u.first_name.lower()
                username = u.username.lower()
                target_str = owner_str.lower()
                
                if (first_name and first_name in target_str) or (username in target_str) or (full_name and target_str in full_name):
                    assigned_user = u
                    break

        action_obj = ActionItem.objects.create(
            meeting=meeting,
            task=a['task'],
            owner_name=owner_str,
            owner_user=assigned_user,
            deadline=a.get('deadline', 'Not specified'),
            priority=a.get('priority', 'Medium'),
            evidence=a.get('evidence', 'Not specified in transcript.'),
            status=a.get('status', 'Pending')
        )
        saved_actions.append(action_obj)
        
        # Dispatch notification to assigned user
        notify_action_assigned(action_obj)

    # 4. Save Unresolved Questions
    saved_questions = []
    for q in extracted_data.get('unresolved_questions', []):
        q_obj = UnresolvedQuestion.objects.create(
            meeting=meeting,
            question=q,
            status='Unresolved'
        )
        saved_questions.append(q_obj)

    # 5. Save Dependencies
    saved_deps = []
    for dep in extracted_data.get('dependencies', []):
        dep_obj = Dependency.objects.create(
            meeting=meeting,
            description=dep
        )
        saved_deps.append(dep_obj)

    return {
        'meeting_id': meeting.id,
        'meeting_title': meeting.title,
        'meeting_summary': extracted_data.get('meeting_summary', ''),
        'decisions_count': len(saved_decisions),
        'actions_count': len(saved_actions),
        'questions_count': len(saved_questions),
        'dependencies_count': len(saved_deps),
        'extracted_data': extracted_data
    }
