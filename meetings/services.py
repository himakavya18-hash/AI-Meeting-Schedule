from datetime import datetime, timedelta, time
from django.db.models import Q
from accounts.models import Availability
from meetings.models import Meeting, MeetingParticipant

def check_single_user_availability(user, target_date, start_time, end_time, exclude_meeting_id=None):
    """
    Checks if a single user is available on a target date and time range.
    Returns (is_available, reason)
    """
    # 1. Global User Status check
    if user.status == 'On Leave':
        return False, "User is on leave"
    if user.status == 'Busy':
        return False, "User marked status as Busy"

    # 2. Weekly Availability / Working Hours check
    day_of_week = target_date.weekday() # 0 = Monday, 6 = Sunday
    weekly_avail = Availability.objects.filter(user=user, day_of_week=day_of_week).first()
    
    if weekly_avail:
        if not weekly_avail.is_available:
            return False, f"Not working on {weekly_avail.get_day_of_week_display()}"
        if start_time < weekly_avail.start_time or end_time > weekly_avail.end_time:
            return False, f"Outside working hours ({weekly_avail.start_time.strftime('%H:%M')} - {weekly_avail.end_time.strftime('%H:%M')})"
    else:
        # Default working hours 09:00 - 17:00
        if start_time < user.work_start_time or end_time > user.work_end_time:
            return False, f"Outside working hours ({user.work_start_time.strftime('%H:%M')} - {user.work_end_time.strftime('%H:%M')})"

    # 3. Existing Meeting Collision check
    query = Q(
        date=target_date,
        start_time__lt=end_time,
        end_time__gt=start_time,
        meeting_participants__user=user,
        meeting_participants__response_status__in=['Accepted', 'Pending']
    )
    if exclude_meeting_id:
        query &= ~Q(id=exclude_meeting_id)

    conflicting_meeting = Meeting.objects.filter(query).exclude(status='Cancelled').first()
    if conflicting_meeting:
        return False, f"Conflicting meeting: '{conflicting_meeting.title}' ({conflicting_meeting.start_time.strftime('%H:%M')}-{conflicting_meeting.end_time.strftime('%H:%M')})"

    return True, "Available"

def check_participants_availability(users, target_date, start_time, end_time, exclude_meeting_id=None):
    """
    Checks availability of a list of users for a given date and time range.
    Returns dict with summary and detailed statuses.
    """
    available_users = []
    unavailable_users = []
    statuses = []

    for user in users:
        is_avail, reason = check_single_user_availability(user, target_date, start_time, end_time, exclude_meeting_id)
        user_info = {
            'id': user.id,
            'username': user.username,
            'name': user.get_full_name() or user.username,
            'email': user.email,
            'is_available': is_avail,
            'reason': reason
        }
        statuses.append(user_info)
        if is_avail:
            available_users.append(user)
        else:
            unavailable_users.append(user)

    all_available = (len(unavailable_users) == 0)
    
    return {
        'all_available': all_available,
        'message': "All participants are available. The meeting can be scheduled." if all_available else "Some participants are unavailable at the selected time.",
        'available_count': len(available_users),
        'unavailable_count': len(unavailable_users),
        'total_count': len(users),
        'statuses': statuses,
        'available_users': available_users,
        'unavailable_users': unavailable_users
    }

def suggest_alternative_time_slots(users, target_date, requested_start_time, requested_end_time, exclude_meeting_id=None):
    """
    Finds alternative time slots on target_date where the maximum number of required participants are available.
    """
    # Calculate duration of requested meeting
    dummy_dt = datetime.combine(target_date, time(0, 0))
    dt1 = datetime.combine(target_date, requested_start_time)
    dt2 = datetime.combine(target_date, requested_end_time)
    duration = dt2 - dt1
    if duration.total_seconds() <= 0:
        duration = timedelta(hours=1)

    # Standard business hours candidate slots from 08:00 to 17:00
    candidate_slots = []
    curr_dt = datetime.combine(target_date, time(8, 0))
    end_of_day = datetime.combine(target_date, time(17, 0))

    while curr_dt + duration <= end_of_day + timedelta(hours=1):
        slot_start = curr_dt.time()
        slot_end = (curr_dt + duration).time()
        
        # Skip requested time slot
        if not (slot_start == requested_start_time and slot_end == requested_end_time):
            candidate_slots.append((slot_start, slot_end))
            
        curr_dt += timedelta(minutes=30) # Scan in 30 min increments

    suggestions = []
    for slot_start, slot_end in candidate_slots:
        avail_list = []
        unavail_list = []

        for user in users:
            is_avail, reason = check_single_user_availability(user, target_date, slot_start, slot_end, exclude_meeting_id)
            u_info = {'id': user.id, 'name': user.get_full_name() or user.username}
            if is_avail:
                avail_list.append(u_info)
            else:
                unavail_list.append({'name': user.get_full_name() or user.username, 'reason': reason})

        suggestions.append({
            'start_time': slot_start.strftime('%H:%M'),
            'end_time': slot_end.strftime('%H:%M'),
            'available_count': len(avail_list),
            'total_count': len(users),
            'available_participants': avail_list,
            'unavailable_participants': unavail_list
        })

    # Sort suggestions by highest available count first
    suggestions.sort(key=lambda x: x['available_count'], reverse=True)
    return suggestions[:5] # Return top 5 alternative time slots
