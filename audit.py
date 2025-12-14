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

def get_audit_trail(entity_type=None, entity_id=None, action=None, user_id=None, limit=100):
    """
    Retrieve audit logs with optional filters.
    
    Args:
        entity_type (str, optional): Filter by entity type
        entity_id (int, optional): Filter by entity ID
        action (str, optional): Filter by action
        user_id (int, optional): Filter by user ID
        limit (int): Maximum number of records to return (default: 100)
    
    Returns:
        list: List of AuditLog objects

    """
    query = AuditLog.query
    
    if entity_type:
        query = query.filter_by(entity_type=entity_type)
    
    if entity_id:
        query = query.filter_by(entity_id=entity_id)
    
    if action:
        query = query.filter_by(action=action)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    # Order by most recent first
    query = query.order_by(AuditLog.timestamp.desc())
    
    # Limit results
    query = query.limit(limit)
    
    return query.all()


