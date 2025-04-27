from pydantic import BaseModel
from datetime import datetime

class IdentificationResponse(BaseModel):
    user_id: int
    specie_id:int
    file_storage_key:str
    date_identified:datetime