from novda.schemas.base import BaseSchema

class Email(BaseSchema):
    title: str

class User(BaseSchema):
    id: int
    name: str
    email: Email = None


user1 = User()