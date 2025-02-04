import json
from typing import Any, overload, Optional


class APIException(Exception):
    status_code: int
    detail: str
    headers: dict
    comment: str | Any = None

    def __init__(self, status_code: int, detail: str, headers: dict = None, comment: str | Any = None) -> None:
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        self.comment = comment

        self.__api_response__ = json.dumps(
            {
                'status_code': self.status_code,
                'detail': self.detail,
                'headers': self.headers,
                'comment': self.comment
            }
        )

    def __str__(self) -> str:
        return f"{self.status_code}: {self.detail}"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"


class SchemaException(BaseException):

    @overload
    def __init__(self, field: Any, *, missing: bool = True):
        ...

    @overload
    def __init__(self, field: Any, *, but_got: str, expected: str):
        ...

    def __init__(self, field: Any, *, missing: bool = False, but_got: Optional[str] = None,
                 expected: Optional[str] = None):
        if missing:
            detail = f'Schema Error - "{field}" is required'
        elif but_got and expected:
            detail = f'Schema Error - "{field}" is {expected} type, but got {but_got} type'
        else:
            detail = 'Schema Error - Invalid input'

        self.__detail = detail
        self.__status_code = 422

    def __str__(self) -> str:
        return self.__detail

    def __repr__(self) -> str:
        return self.__detail

    def __as_api_exception__(self) -> APIException:
        return APIException(self.__status_code, detail=self.__detail)
