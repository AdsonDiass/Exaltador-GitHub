from pydantic import BaseModel

class Prompt(BaseModel):
    texto: str
