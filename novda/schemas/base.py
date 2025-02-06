import json
from typing import Union, get_origin, get_args, Any, get_type_hints, ForwardRef

from ..exceptions import SchemaException


class BaseSchemaMeta(type):
    def __repr__(cls):
        def format_field(k, v):
            """Recursively format nested schema fields."""
            if isinstance(v, str):
                return f"{k}: {v}"  # Handle forward references as string
            if hasattr(v, "__annotations__"):  # If it's a schema, recurse
                nested_fields = ", ".join(format_field(nk, nv) for nk, nv in v.__annotations__.items())
                return f"{k}: {v.__name__}({nested_fields})"
            return f"{k}: {v.__name__}"

        fields = ", ".join(format_field(k, v) for k, v in cls.__annotations__.items())
        return f"{cls.__name__}({fields})"



class BaseSchema(metaclass=BaseSchemaMeta):
    def __init__(self, **kwargs):
        annotations = get_type_hints(self.__class__)
        # print(annotations)

        for field, field_type in annotations.items():
            has_default = hasattr(type(self), field)

            if field in kwargs:
                if not self._validate_type(kwargs[field], field_type):
                    raise SchemaException(field, but_got=kwargs[field].__class__.__name__, expected=field_type.__name__)

                setattr(self, field, kwargs[field])

            elif has_default:
                if getattr(type(self), field, None) is not None:
                    if not self._validate_type(getattr(type(self), field), field_type):
                        raise SchemaException(field, but_got=getattr(type(self), field).__class__.__name__, expected=field_type.__name__)
                setattr(self, field, getattr(type(self), field))

            else:
                raise SchemaException(field, missing=True)

        self.validate()

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

    def validate(self) -> None:
        ...


    @staticmethod
    def _validate_type(value, expected_type, schema_cls=None):
        """Validate value against expected type, resolving forward references"""

        # Resolve forward references
        if isinstance(expected_type, str):
            if schema_cls is not None:
                type_hints = get_type_hints(schema_cls)
                expected_type = type_hints.get(expected_type, expected_type)

        if isinstance(expected_type, ForwardRef):  # Python < 3.9 uses ForwardRef
            expected_type = expected_type._evaluate(globals(), locals(), frozenset())

        origin = get_origin(expected_type)

        if origin is None:
            return isinstance(value, expected_type)

        elif origin is Union:
            return any(BaseSchema._validate_type(value, arg, schema_cls) for arg in get_args(expected_type))

        elif origin is list:
            if not isinstance(value, list):
                return False
            element_type = get_args(expected_type)[0]
            return all(BaseSchema._validate_type(item, element_type, schema_cls) for item in value)

        return False

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"

    def __iter__(self):
        yield from self.__dict__.items()


