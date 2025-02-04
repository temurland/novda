from ..exceptions.base import APIException


class SchemaException(APIException):

    def __init__(self, status_code: int, detail: str, headers: dict = None, comment: str | Any = None) -> None:
        pass