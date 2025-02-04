import json
from types import UnionType
from typing import Union, get_origin, get_args, Optional, List, Any, Iterable, Annotated


class BaseSchemaMeta(type):
    def __repr__(cls):
        fields = ", ".join(f"{k}: {v.__name__}" for k, v in cls.__annotations__.items())
        return f"{cls.__name__}({fields})"

class BaseSchema(metaclass=BaseSchemaMeta):
    def __init__(self, **kwargs):
        annotations = self.__annotations__

        for field, field_type in annotations.items():
            has_default = hasattr(self, field)

            if field in kwargs:
                if not self._validate_type(kwargs[field], field_type):
                    raise TypeError(
                        f"Invalid type for field '{field}', expected {field_type}, got {type(kwargs[field])}"
                    )
                setattr(self, field, kwargs[field])

            elif not has_default:
                raise ValueError(f"Missing required field: {field}")


    def as_dict(self) -> dict[str, Any]:
        result = {}
        for field, value in self.__dict__.items():
            if isinstance(value, BaseSchema):
                result[field] = value.as_dict()
            elif isinstance(value, list):
                result[field] = [item.as_dict() if isinstance(item, BaseSchema) else item for item in value]
            else:
                result[field] = value
        return result

    def dump_json(self) -> str:
        return json.dumps(self.as_dict())

    def __iter__(self):
        yield from self.__dict__.items()

    @staticmethod
    def _validate_type(value, expected_type):
        origin = get_origin(expected_type)

        if origin is None:
            return isinstance(value, expected_type)

        elif origin is Union or origin is UnionType:
            return any(BaseSchema._validate_type(value, arg) for arg in get_args(expected_type))

        elif origin is list:
            if not isinstance(value, list):
                return False
            element_type = get_args(expected_type)[0]
            return all(BaseSchema._validate_type(item, element_type) for item in value)

        return False

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"


def validate_phone(number: str) -> bool:
    print(number)
    return True

class User(BaseSchema):
    phone: Annotated[str, validate_phone]

user1 = User(phone="+91123456789")