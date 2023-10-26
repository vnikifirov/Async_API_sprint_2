import uuid
import datetime
from typing import List
from models.orjson import BaseOrjsonModel

class Film(BaseOrjsonModel):
    id: uuid
    title: str
    description: str
    creation_date: datetime
    rating: float
    type: str
    genres: List[str]
    actors: List[str]
    directors = List[str]
    screenwriters = List[str]
        
        