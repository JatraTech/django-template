from drf_standardized_errors.formatter import ExceptionFormatter as ExceptionFormatter_
from drf_standardized_errors.types import ErrorResponse


class ExceptionFormatter(ExceptionFormatter_):
    def format_error_response(self, error_response: ErrorResponse):
        error = error_response.errors[0]
        return {
            "success": False,
            "type": error_response.type,
            "code": error.code,
            "error": error.detail,
            "field": error.attr,
            "index": None,
        }


class ScrappingException(Exception):
    def __init__(self,message="",data={},*args: object) -> None:
        super().__init__(
            message,
            *args
        )
        self.data = data