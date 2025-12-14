import json
from flask import request
from database import db, AuditLog



def log_audit(action, entity_type, entity_id, user_id=None, details=None):
    """
    Create an audit log entry for system actions.
    
    Args:
        action (str): The action performed (e.g., 'loan_created', 'book_returned')
        entity_type (str): Type of entity affected (e.g., 'loan', 'book', 'user')
        entity_id (int): ID of the affected entity
        user_id (int, optional): ID of the user who performed the action
        details (dict, optional): Additional context as a dictionary
    
    Returns:
        AuditLog: The created audit log entry
    
    """
    # Get IP address from request context (if available)
    ip_address = None
    try:
        ip_address = request.remote_addr
    except RuntimeError:
        ip_address = None
    
    # Convert details dict to JSON string
    details_json = None
    if details:
        try:
            details_json = json.dumps(details)
        except (TypeError, ValueError):
            details_json = str(details)
    
    # Create audit log entry
    audit = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        details=details_json,
        ip_address=ip_address
    )
    
    db.session.add(audit)
    
    return audit