import re
from pathlib import Path
from typing import Iterator, List, Optional
from uuid import uuid4

from dagster import (DynamicOut, DynamicOutput, Field, Out, get_dagster_logger, Output,
                     op)

from dino.models.file import FileModel
from dino.utils.filesystem import get_file_informations


def check_file_matches_patterns(file, patterns):
    if not patterns:
        return False
    for pattern in patterns:
        if re.match(pattern, file):
            return True
    return False

@op(
    config_schema={
        "source_path": Field(str, description="Find all files from a given path"),
        "recurse": Field(
            bool, description="Whether or not to recurse subfolders", default_value=True
        ),
        "file_magic": Field(
            str, description="Find files of a given type", default_value=".*"
        ),
        "file_names_regexes": Field(
            [str],
            description="Find filenames matching specific patterns",
            default_value=[".*"],
        ),
    },
    out=DynamicOut(Path),
)
def generate_files(context) -> Iterator[Path]:
    """Gather files from a given path."""
    logger = get_dagster_logger()

    logger.info(
        f"Gather files from {context.op_config['source_path']} using magic {context.op_config['file_magic']} and patterns {context.op_config['file_names_regexes']}"
    )

    path = Path(context.op_config["source_path"])
    if path.is_file():
        entries = [path]
    else:
        if context.op_config["recurse"]:
            entries = path.glob("**/*")
        else:
            entries = path.glob("*")

    
    if context.op_config["file_names_regexes"]:
        check_file_pattern = any(i != ".*" for i in context.op_config["file_names_regexes"])
    else:
        check_file_pattern = False

    check_file_magic = context.op_config["file_magic"] != ".*"
    file_patterns_matching = [re.compile(i) for i in context.op_config["file_names_regexes"]]

    for entry in entries:
        entry_absolute_str = str(entry.absolute())
        if (
            "__DINO_TEMP" in entry_absolute_str
            or "DINO_SPLUNK_UNIVERSAL_FORWARDER" in entry_absolute_str
            or not entry.is_file()
        ):
            continue

        if check_file_pattern:
            if not check_file_matches_patterns(entry.name, file_patterns_matching):
                continue
            else:
                logger.debug(f"File {entry.name} Matched one of patterns")

        file_info = get_file_informations(entry)

        if check_file_magic and context.op_config["file_magic"] not in file_info.magic:
            logger.debug(
                f"File {entry.name} has invalid magic (expected: {context.op_config['file_magic']})"
            )
            continue
        logger.info(f"Found file {entry}")
        yield DynamicOutput(value=entry, mapping_key=uuid4().hex)


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
    out={"file": Out(Path, is_required=False)},
)
def find_file(context, folder: Path):
    """Find a file in a given folder."""
    logger = get_dagster_logger()
    if context.op_config["skip"]:
        logger.info(f"Skipping execution of find_file for {folder}")
        return
    logger.debug(
        f"Searching for a file {context.op_config['file_names_patterns']} in {folder})"
    )

    for filename in context.op_config["file_names_patterns"]:
        potential_file = folder / filename
        if potential_file.is_file():
            logger.info(f"Found file {potential_file}")
            yield Output(potential_file, "file")
            return
            #return get_file_informations(potential_file)

    logger.critical(
        f"Could not find one of {context.op_config['file_names_patterns']} from {folder}"
    )
    # raise ValueError(
    #     f"Could not find one of {context.op_config['file_names_patterns']} from {folder}"
    # )


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
)
def find_files(context, folder: Path) -> List[Path]:
    """Find files in a given folder."""
    logger = get_dagster_logger()
    if context.op_config["skip"]:
        logger.info(f"Skipping execution of find_files for {folder}")
        return []
    logger.debug(
        f"Searching for files matching {context.op_config['file_names_patterns']} in {folder})"
    )
    files = []
    for pattern in context.op_config["file_names_patterns"]:
        files.extend(folder.rglob(pattern))

    logger.info(f"found {len(files)}")
    return files


