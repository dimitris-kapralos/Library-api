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

def format_audit_log(audit_log):
    """
    Format an AuditLog object as a dictionary for API responses.
    
    Args:
        audit_log (AuditLog): The audit log to format
    
    Returns:
        dict: Formatted audit log data
    """
    # Parse details JSON back to dict
    details = None
    if audit_log.details:
        try:
            details = json.loads(audit_log.details)
        except (json.JSONDecodeError, TypeError):
            details = audit_log.details
    
    return {
        'id': audit_log.id,
        'action': audit_log.action,
        'entity_type': audit_log.entity_type,
        'entity_id': audit_log.entity_id,
        'user_id': audit_log.user_id,
        'timestamp': audit_log.timestamp.isoformat(),
        'details': details,
        'ip_address': audit_log.ip_address
    }


# Common action names 
class AuditAction:
    """Constants for audit action names"""
    USER_CREATED = 'user_created'
    BOOK_CREATED = 'book_created'
    BOOK_UPDATED = 'book_updated'
    LOAN_CREATED = 'loan_created'
    LOAN_RETURNED = 'loan_returned'
    FINE_CALCULATED = 'fine_calculated'
    LOAN_OVERDUE = 'loan_overdue'

