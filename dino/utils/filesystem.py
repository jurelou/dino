from pathlib import Path
from typing import Iterator, List

import magic

from dino.models.file import FileModel


def get_file_informations(filepath: Path) -> FileModel:
    return FileModel(path=filepath, magic=magic.from_file(str(filepath.absolute())))


def find_files_matching_patterns(folder: Path, patterns: List[str]) -> Iterator[Path]:
    for pattern in patterns:
        for f in folder.rglob(pattern):
            yield f
