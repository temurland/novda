import json
from typing import Any


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
