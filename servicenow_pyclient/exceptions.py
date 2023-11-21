class SNException(Exception):
    error_msg = '<empty>'
    error_type = '<empty>'
    error_detail = '<empty>'

    def __init__(self, req_error, sn_error):
        error = sn_error.get('error', {})

        if 'message' in error:
            self.error_msg = error['message'] or self.error_msg
        if 'type' in error:
            self.error_type = error['type'] or self.error_type
        if 'detail' in error:
            self.error_detail = error['detail'] or self.error_detail

    def __str__(self):
        return f'Message: "{self.error_msg}" Type: "{self.error_type}" Details: "{self.error_detail}"'


class SNEmptyContent(SNException):

    def __init__(self, req_error, sn_error):
        super().__init__(req_error=req_error, sn_error=sn_error)
