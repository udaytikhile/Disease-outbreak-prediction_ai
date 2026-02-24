"""
Standardized API Response Helpers.

Provides a consistent JSON response envelope across all endpoints.
Every API response follows the format:
    { "success": bool, "data"|"error": ..., "meta"?: ... }

Usage:
    from src.utils.response import success_response, error_response

    return success_response({'user': user_dict})
    return error_response('Validation failed', status=400, details=err.messages)
"""
from flask import jsonify


def success_response(data=None, status=200, meta=None):
    """Create a standardized success JSON response.

    Args:
        data: Response payload (dict, list, or None)
        status: HTTP status code (default 200)
        meta: Optional metadata dict (pagination, timing, etc.)

    Returns:
        tuple: (Response, status_code)
    """
    body = {'success': True}
    if data is not None:
        body['data'] = data
    if meta is not None:
        body['meta'] = meta
    return jsonify(body), status


def error_response(message, status=400, details=None):
    """Create a standardized error JSON response.

    Args:
        message: Human-readable error message
        status: HTTP status code (default 400)
        details: Optional dict with field-level error details

    Returns:
        tuple: (Response, status_code)
    """
    body = {'success': False, 'error': message}
    if details is not None:
        body['details'] = details
    return jsonify(body), status
