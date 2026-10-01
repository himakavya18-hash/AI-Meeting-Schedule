import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_meeting_invitation_email(meeting, participant):
    """
    Sends meeting invitation email to a participant.
    """
    subject = f"Meeting Scheduled: {meeting.title}"
    message = f"""
Dear {participant.get_full_name() or participant.username},

You have been invited to a meeting by {meeting.organizer.get_full_name() or meeting.organizer.username}.

Meeting Details:
- Title: {meeting.title}
- Organizer: {meeting.organizer.get_full_name() or meeting.organizer.username}
- Type: {meeting.meeting_type}
- Priority: {meeting.priority}
- Date: {meeting.date}
- Time: {meeting.start_time} - {meeting.end_time}
- Agenda: {meeting.agenda or 'N/A'}

Please confirm your attendance in the portal:
http://localhost:8000/meetings/{meeting.id}/

Best regards,
Company Meeting Portal Team
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[participant.email],
            fail_silently=True
        )
        logger.info(f"Sent meeting invitation email to {participant.email}")
    except Exception as e:
        logger.error(f"Error sending meeting invitation email to {participant.email}: {e}")

def send_availability_report_email(meeting, available_users, unavailable_users, alternative_slots):
    """
    Sends availability report email to meeting organizer.
    """
    organizer = meeting.organizer
    subject = f"Meeting Availability Report: {meeting.title}"
    
    avail_names = "\n".join([f" - {u.get_full_name() or u.username}" for u in available_users]) or " None"
    unavail_names = "\n".join([f" - {u.get_full_name() or u.username}" for u in unavailable_users]) or " None"
    
    slots_str = ""
    for slot in alternative_slots:
        slots_str += f" - {slot['start_time']} to {slot['end_time']} ({slot['available_count']} participants available)\n"
    if not slots_str:
        slots_str = " No alternative slots found."

    message = f"""
Dear {organizer.get_full_name() or organizer.username},

Here is the participant availability report for your requested meeting: "{meeting.title}" on {meeting.date} ({meeting.start_time} - {meeting.end_time}).

Available Participants ({len(available_users)}):
{avail_names}

Unavailable Participants ({len(unavailable_users)}):
{unavail_names}

Suggested Alternative Time Slots:
{slots_str}

You can update or reschedule the meeting directly in the portal:
http://localhost:8000/meetings/{meeting.id}/

Best regards,
Company Meeting Portal Team
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[organizer.email],
            fail_silently=True
        )
        logger.info(f"Sent availability report email to organizer {organizer.email}")
    except Exception as e:
        logger.error(f"Error sending availability report email: {e}")

def send_action_assigned_email(action):
    """
    Sends email notification when an action item is assigned.
    """
    if not action.owner_user:
        return
        
    subject = f"New Action Item Assigned: {action.task}"
    message = f"""
Dear {action.owner_user.get_full_name() or action.owner_user.username},

A new action item has been assigned to you from meeting "{action.meeting.title}".

Task: {action.task}
Deadline: {action.deadline}
Priority: {action.priority}
Status: {action.status}

Evidence from Transcript:
"{action.evidence or 'N/A'}"

Please manage your tasks on your Action Dashboard:
http://localhost:8000/actions/my/

Best regards,
Company Meeting Portal Team
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[action.owner_user.email],
            fail_silently=True
        )
    except Exception as e:
        logger.error(f"Error sending action assignment email: {e}")
