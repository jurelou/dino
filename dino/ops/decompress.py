import lzma
from pathlib import Path
from typing import List

import py7zr
from dagster import Field, get_dagster_logger, op

from dino import layout_manager
from dino.models.file import FileModel


def decompress_7z(filepath: Path, passwords: List[str] = []):
    logger = get_dagster_logger()

    output_folder = layout_manager.make_temp_dir(filepath)
    output_folder_str = str(output_folder.absolute())
    with py7zr.SevenZipFile(filepath, mode="r") as archive:
        if not archive.needs_password():
            archive.extractall(path=output_folder_str)
            logger.info(
                f"Extract unencrypted 7z file {filepath.absolute()} to {output_folder_str}"
            )
            return output_folder

    for password in passwords:
        try:
            with py7zr.SevenZipFile(filepath, mode="r", password=password) as archive:
                archive.extractall(path=output_folder_str)
            logger.info(
                f"Extracted encrypted 7z file {filepath.absolute()} to {output_folder_str} with password `{password}`"
            )
            return output_folder
        except lzma.LZMAError as err:
            logger.debug(f"Could not decrypt {filepath.absolute()} with `{password}`")
    raise ValueError(
        f"Could not decrypt 7z file {filepath.absolute()} with passwords: {passwords}"
    )


@op(
    config_schema={
        "passwords": Field(
            [str],
            description="List of passwords for encrypted archives",
            default_value=["avproof", "infected", "virus"],
        ),
    },
)
def decompress_file(context, file: FileModel) -> Path:
    logger = get_dagster_logger()
    mapping = {
        "7-zip archive data": decompress_7z,
    }
    for algo, decompress_method in mapping.items():
        if algo in file.magic:
            logger.info(
                f"Decompress {file.path} using method `{decompress_method.__name__}`"
            )
            return decompress_method(file.path, context.op_config["passwords"])
    logger.critical(f"Could not decompress file {file}")
    raise ValueError(f"Could not decompress file {file}")
