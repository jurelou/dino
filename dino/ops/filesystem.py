import re
from pathlib import Path
from typing import Iterator, List
from uuid import uuid4

from dagster import (DynamicOut, DynamicOutput, Field, Out, get_dagster_logger,
                     op)

from dino.models.file import FileModel
from dino.utils.filesystem import get_file_informations


@op(
    config_schema={
        "source_path": Field(str, description="Find all files from a given path"),
        "recurse": Field(
            bool, description="Whether or not to recurse subfolders", default_value=True
        ),
        "file_magic": Field(
            str, description="Find files of a given type", default_value=".*"
        ),
        "file_name_regex": Field(
            str,
            description="Find filenames matching a specific pattern",
            default_value=".*",
        ),
    },
    out=DynamicOut(FileModel),
)
def gather_files(context) -> Iterator[FileModel]:
    """Gather files from a given path."""
    logger = get_dagster_logger()

    logger.info(
        f"Gather files from {context.op_config['source_path']} using magic {context.op_config['file_magic']} and path {context.op_config['file_name_regex']}"
    )

    path = Path(context.op_config["source_path"])
    if path.is_file():
        entries = [path]
    else:
        if context.op_config["recurse"]:
            entries = path.glob("**/*")
        else:
            entries = path.glob("*")

    file_pattern_matching = re.compile(context.op_config["file_name_regex"])
    check_file_pattern = context.op_config["file_name_regex"] != ".*"
    check_file_magic = context.op_config["file_magic"] != ".*"

    for entry in entries:
        entry_absolute_str = str(entry.absolute())
        if (
            "__DINO_TEMP" in entry_absolute_str
            or "DINO_SPLUNK_UNIVERSAL_FORWARDER" in entry_absolute_str
            or not entry.is_file()
        ):
            continue

        if check_file_pattern and not re.match(file_pattern_matching, entry.name):
            logger.debug(
                f"File {entry_absolute_str} has an invalid name (expected: {context.op_config['file_name_regex']})"
            )
            continue

        file_info = get_file_informations(entry)

        if check_file_magic and context.op_config["file_magic"] not in file_info.magic:
            logger.debug(
                f"File {entry_absolute_str} has invalid magic (expected: {context.op_config['file_magic']})"
            )
            continue
        logger.info(f"Found file {entry}")
        yield DynamicOutput(value=file_info, mapping_key=uuid4().hex)


@op(
    config_schema={
        "file_names_patterns": Field(
            [str], description="Find a single file matching a specific pattern"
        ),
        "skip": Field(
            bool,
            description="Whether or not to skip execution of this op (returns nothing)",
            default_value=False,
        ),
    },
    out=Out(FileModel, is_required=False),
)
def find_file(context, folder: Path):
    """Find a file in a given folder."""
    logger = get_dagster_logger()
    if context.op_config["skip"]:
        logger.info(f"Skipping execution of find_file for {folder}")
        return None
    logger.debug(
        f"Searching for a file {context.op_config['file_names_patterns']} in {folder})"
    )

    for filename in context.op_config["file_names_patterns"]:
        potential_file = folder / filename
        if potential_file.is_file():
            logger.info(f"Found file {potential_file}")
            return get_file_informations(potential_file)

    logger.critical(
        f"Could not find one of {context.op_config['file_names_patterns']} from {folder}"
    )
    raise ValueError(
        f"Could not find one of {context.op_config['file_names_patterns']} from {folder}"
    )
