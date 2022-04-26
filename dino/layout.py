import os
import uuid
from pathlib import Path, PurePath


class LayoutManager:
    def __init__(self):
        self._root_folder = Path("/DINO_ROOT")  # Path(settings.root_folder)

        self._temp_folder = self._root_folder / "__DINO_TEMP"
        self._temp_folder.mkdir(parents=True, exist_ok=True)

        self._uf_folder = self._root_folder / "DINO_SPLUNK_UNIVERSAL_FORWARDER"
        self._uf_folder.mkdir(parents=True, exist_ok=True)

    def _canonicalize_path(self, path: Path) -> PurePath:
        parts = PurePath(path).parts

        if self._temp_folder.name in parts:
            return Path(*parts[parts.index(self._temp_folder.name) + 1 : -1])
        if self._uf_folder.name in parts:
            return Path(*parts[parts.index(self._uf_folder.name) + 1 : -1])

        if self._root_folder.name in parts:
            return Path(*parts[parts.index(self._root_folder.name) + 1 : -1])
        return Path(*parts[1:-1])

    def make_temp_dir(self, path: Path, create: bool = True):
        """Creates a temporary folder from a given path."""
        tmp_path = (
            self._temp_folder
            / self._canonicalize_path(path)
            / f"{path.stem}_{uuid.uuid4().hex}"
        )
        if create:
            tmp_path.mkdir(parents=True, exist_ok=True)
        return tmp_path

    # def make_splunk_uf_dir(self, path: Path, subfolder: str, create: bool = True):
    #     """Creates a splunk universal forwarder folder from a given path."""
    #     uf_path = self._uf_folder / subfolder / self._canonicalize_path(path) / path.stem
    #     if create:
    #         uf_path.mkdir(parents=True, exist_ok=True)
    #     return uf_path
