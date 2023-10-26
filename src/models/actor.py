from .person import Person
from models.orjson import BaseOrjsonModel

class Actor(Person, BaseOrjsonModel):
    pass