from pathlib import Path
from typing import List
import subprocess

import py7zr
from dagster import Field, get_dagster_logger, op

from dino import layout_manager
from dino.models.file import FileModel
from dino.utils.filesystem import get_file_informations


def decompress_7z(filepath: Path, passwords: List[str] = []):
    logger = get_dagster_logger()

    output_folder = layout_manager.make_temp_dir(filepath)
    encrypted = False

    with py7zr.SevenZipFile(filepath, mode="r") as archive:
        encrypted = archive.needs_password()

    # if not encrypted:
    command = ["7z", "x", filepath.absolute(), f"-o{output_folder.absolute()}", "-y", "-bd"]

    res = subprocess.run(command, capture_output=True)
    logger.debug(res.stdout.decode("utf-8", "replace"))
    logger.info(f"Executed `{command}` Return code: {res.returncode}")
    if res.returncode != 0:
        logger.critical(res.stderr.decode("utf-8", "replace"))
        raise Exception("Error while executing 7z extract.")
    return output_folder


    # if not encrypted:
    #     logger.info(f"------ {targets}")
    #     with py7zr.SevenZipFile(filepath, mode="r") as archive:
    #         logger.info(
    #             f"Extract unencrypted 7z file {filepath.absolute()} to {output_folder_str}"
    #         )
    #         archive.extract(path=output_folder_str, targets=targets)
    #     return output_folder_str

    # for password in passwords:
    #     try:
    #         with py7zr.SevenZipFile(filepath, mode="r", password=password) as archive:
    #             archive.extractall(path=output_folder_str)
    #         logger.info(
    #             f"Extracted encrypted 7z file {filepath.absolute()} to {output_folder_str} with password `{password}`"
    #         )
    #         return output_folder
    #     except lzma.LZMAError as err:
    #         logger.debug(f"Could not decrypt {filepath.absolute()} with `{password}`")
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
def decompress_file(context, file: Path) -> Path:
    logger = get_dagster_logger()
    mapping = {
        "7-zip archive data": decompress_7z,
    }
    file_info = get_file_informations(file)
    for algo, decompress_method in mapping.items():
        if algo in file_info.magic:
            logger.info(
                f"Decompress {file_info.path} using method `{decompress_method.__name__}`"
            )
            return decompress_method(file_info.path, context.op_config["passwords"])
    logger.critical(f"Could not decompress file {file_info}")
    raise ValueError(f"Could not decompress file {file_info}")
