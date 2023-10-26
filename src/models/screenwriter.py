import orjson

def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()

from models.person import Person
from models.orjson import BaseOrjsonModel

class Screenwriter(Person, BaseOrjsonModel):
    pass