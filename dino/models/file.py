from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class FileType(Enum):
    # Compression file types
    XZ = 0
    ZIP = 1
    GZIP = 2
    BZIP2 = 3
    SEVENZIP = 4

    # Applications
    RAM = 10

    UNKNOWN = 1000


class FileModel(BaseModel):
    path: Path
    magic: str
