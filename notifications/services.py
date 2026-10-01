from notifications.models import Notification
from notifications.email_service import (
    send_meeting_invitation_email,
    send_availability_report_email,
    send_action_assigned_email
)

def create_notification(user, title, message, link=None, send_email=True):
    """
    Creates an in-app notification and optionally triggers email.
    """
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        link=link
    )
    return notification

def notify_meeting_created(meeting, available_users, unavailable_users, alternative_slots):
    """
    Dispatches notifications and emails for a newly created meeting.
    """
    # 1. Notify organizer with availability report
    report_title = f"Availability Report: {meeting.title}"
    if not unavailable_users:
        report_msg = f"All {len(available_users)} participants are available for your meeting on {meeting.date} at {meeting.start_time}."
    else:
        report_msg = f"{len(unavailable_users)} participant(s) are unavailable on {meeting.date} at {meeting.start_time}. {len(alternative_slots)} alternative slots suggested."
    
    create_notification(
        user=meeting.organizer,
        title=report_title,
        message=report_msg,
        link=f"/meetings/{meeting.id}/"
    )
    send_availability_report_email(meeting, available_users, unavailable_users, alternative_slots)

    # 2. Notify participants
    for participant in meeting.participants.all():
        if participant != meeting.organizer:
            create_notification(
                user=participant,
                title=f"Invitation: {meeting.title}",
                message=f"You are invited by {meeting.organizer.get_full_name() or meeting.organizer.username} for {meeting.date} ({meeting.start_time} - {meeting.end_time}).",
                link=f"/meetings/{meeting.id}/"
            )
            send_meeting_invitation_email(meeting, participant)

def notify_action_assigned(action):
    """
    Notifies an employee when an action item is assigned to them.
    """
    if action.owner_user:
        create_notification(
            user=action.owner_user,
            title=f"New Action Item: {action.task[:40]}",
            message=f"Task assigned from meeting '{action.meeting.title}'. Deadline: {action.deadline}",
            link=f"/actions/my/"
        )
        send_action_assigned_email(action)
