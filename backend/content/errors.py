"""Safe parser failures; callers must not log source text."""
class ContentError(ValueError):
    status_code = 422

    def __init__(self, message, code='CONTENT_INVALID', source_span=None):
        super().__init__(message)
        self.code = code
        self.source_span = source_span

    def as_error(self, request_id):
        error = {'code': self.code, 'message': str(self), 'requestId': request_id}
        if self.source_span is not None:
            error['fieldErrors'] = {'body': [{'message': str(self), 'sourceSpan': self.source_span}]}
        return error
