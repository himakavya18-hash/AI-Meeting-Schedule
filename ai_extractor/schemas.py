import json
import logging

logger = logging.getLogger(__name__)

REQUIRED_KEYS = ["meeting_summary", "decisions", "action_items", "unresolved_questions", "dependencies", "discussion_points"]

def validate_extraction_schema(data):
    """
    Validates that the extracted dictionary matches the mandatory schema format.
    Returns (is_valid, cleaned_data_or_error_message).
    """
    if not isinstance(data, dict):
        return False, "Output must be a JSON object"

    cleaned = {
        "meeting_summary": str(data.get("meeting_summary", "")),
        "decisions": [],
        "action_items": [],
        "unresolved_questions": [],
        "dependencies": [],
        "discussion_points": []
    }

    # Validate decisions
    decisions = data.get("decisions", [])
    if isinstance(decisions, list):
        for item in decisions:
            if isinstance(item, dict) and "decision" in item:
                cleaned["decisions"].append({
                    "decision": str(item.get("decision", "")),
                    "evidence": str(item.get("evidence", "Not specified in transcript.")),
                    "confidence": float(item.get("confidence", 0.90))
                })

    # Validate action items
    action_items = data.get("action_items", [])
    if isinstance(action_items, list):
        for item in action_items:
            if isinstance(item, dict) and "task" in item:
                cleaned["action_items"].append({
                    "task": str(item.get("task", "")),
                    "owner": str(item.get("owner", "Not specified")),
                    "deadline": str(item.get("deadline", "Not specified")),
                    "priority": str(item.get("priority", "Medium")),
                    "evidence": str(item.get("evidence", "Not specified in transcript.")),
                    "status": str(item.get("status", "Pending"))
                })

    # Validate lists
    for key in ["unresolved_questions", "dependencies", "discussion_points"]:
        val_list = data.get(key, [])
        if isinstance(val_list, list):
            cleaned[key] = [str(x) for x in val_list if x]

    return True, cleaned
