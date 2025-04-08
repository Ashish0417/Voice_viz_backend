
from pydantic import BaseModel
from typing import Any, Dict, List

class DataRequest(BaseModel):
    data: List[Dict[str, Any]]
    notes: str  # <-- new field
    
class GraphResponse(BaseModel):
    title: str
    image_base64: str
