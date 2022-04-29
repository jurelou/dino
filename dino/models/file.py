from pathlib import Path
from pydantic import BaseModel


class FileModel(BaseModel):
    path: Path
    magic: str
