import uuid
import datetime
from models.orjson import BaseOrjsonModel

class Genre(BaseOrjsonModel):
    id: uuid
    name: str
    created: datetime
    modified: datetime