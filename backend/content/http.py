"""HTTP failure mapping for future parser consumers; no publish endpoint exists."""
from rest_framework.response import Response


def content_error_response(error, request_id):
    return Response(error.as_error(request_id), status=error.status_code)
