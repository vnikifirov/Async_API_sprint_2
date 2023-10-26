import uuid
import datetime
from models.orjson import BaseOrjsonModel

class Person(BaseOrjsonModel):
    id: uuid
    full_name: str
    gender: str
    created: datetime
    modified: datetime
   