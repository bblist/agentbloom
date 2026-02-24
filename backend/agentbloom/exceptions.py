"""
Custom DRF exception handler.

Catches Django IntegrityError (duplicate key, constraint violations)
and returns a 400 Bad Request with a descriptive JSON error instead
of an opaque 500 Server Error.
"""

from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Extends DRF's default handler with IntegrityError support.
    """
    # Let DRF handle its own exceptions first
    response = exception_handler(exc, context)
    if response is not None:
        return response

    # Handle database integrity errors (duplicate keys, NOT NULL, etc.)
    if isinstance(exc, IntegrityError):
        detail = str(exc)
        # Extract a user-friendly message
        if "duplicate key" in detail or "unique constraint" in detail.lower():
            # Try to extract the constraint/field name
            msg = "A record with this data already exists."
            if "Key (" in detail:
                try:
                    key = detail.split("Key (")[1].split(")")[0]
                    val = detail.split("=(")[1].split(")")[0] if "=(" in detail else ""
                    msg = f"Duplicate value for '{key}': {val}"
                except (IndexError, ValueError):
                    pass
            return Response(
                {"detail": msg, "code": "duplicate"},
                status=status.HTTP_409_CONFLICT,
            )
        elif "null value" in detail or "not-null" in detail.lower():
            return Response(
                {"detail": "A required field was missing.", "code": "null_violation"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {"detail": "Data integrity error.", "code": "integrity_error"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return None
