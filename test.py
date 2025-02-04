from novda.exceptions import SchemaException, APIException
from novda.schemas.base import BaseSchema

class Email(BaseSchema):
    user: 'User' = None
    title: str

class User(BaseSchema):
    id: int
    name: str
    email: Email = None

    # def validate(self) -> None:
    #     raise APIException(422, 'test')


user = User(id=1, name='test')
user2 = User(id=1, name='test')
user.email = Email(user=user2, title='<EMAIL>')
print(user)