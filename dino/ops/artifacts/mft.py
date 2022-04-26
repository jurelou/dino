from pathlib import Path

from dagster import Field, get_dagster_logger, op
from mft import PyMftAttributeX10, PyMftAttributeX30, PyMftParser

from dino.utils.filesystem import find_files_matching_patterns


def parse_mft_file(path: Path):
    parser = PyMftParser(str(path.absolute()))
    for entry_or_error in parser.entries():
        if isinstance(entry_or_error, RuntimeError):
            continue
        for attribute_or_error in entry_or_error.attributes():
            if isinstance(attribute_or_error, RuntimeError):
                continue
            resident_content = attribute_or_error.attribute_content
            if not resident_content:
                continue
            if isinstance(resident_content, PyMftAttributeX10):
                yield {
                    "type": "Standard_Information",
                    "accessed": resident_content.accessed.isoformat(),
                    "class_id": resident_content.class_id,
                    "created": resident_content.created.isoformat(),
                    "file_flags": resident_content.file_flags,
                    "max_version": resident_content.max_version,
                    "mft_modified": resident_content.mft_modified.isoformat(),
                    "modified": resident_content.modified.isoformat(),
                    "owner_id": resident_content.owner_id,
                    "quota": resident_content.quota,
                    "security_id": resident_content.security_id,
                    "usn": resident_content.usn,
                    "version": resident_content.version,
                }
            if isinstance(resident_content, PyMftAttributeX30):
                yield {
                    "type": "File_Name",
                    "accessed": resident_content.accessed.isoformat(),
                    "created": resident_content.created.isoformat(),
                    "flags": resident_content.flags,
                    "logical_size": resident_content.logical_size,
                    "mft_modified": resident_content.mft_modified.isoformat(),
                    "modified": resident_content.modified.isoformat(),
                    "name": resident_content.name,
                    "namespace": resident_content.namespace,
                    "parent_entry_id": resident_content.parent_entry_id,
                    "parent_entry_sequence": resident_content.parent_entry_sequence,
                    "physical_size": resident_content.physical_size,
                    "reparse_value": resident_content.reparse_value,
                }


@op(
    required_resource_keys={"splunk"},
    config_schema={
        "file_names_regex": Field(
            [str], description="MFT file names regex.", default_value=["*_$MFT_*"]
        ),
    },
)
def process_mft(context, folder: Path):
    """Parses MFT against a folder of files."""
    logger = get_dagster_logger()
    logger.info(
        f"Process mft from `{folder}` with files matching `{context.op_config['file_names_regex']}`"
    )

    for f in find_files_matching_patterns(
        folder, context.op_config["file_names_regex"]
    ):
        with context.resources.splunk.stream(
            sourcetype="dino:mft/json",
            host=str(f.absolute()),
            source="mft",
        ) as hec:
            for entry in parse_mft_file(f):
                hec.send_dict(entry)
