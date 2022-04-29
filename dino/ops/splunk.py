import csv
from pathlib import Path
import sys

import ujson
from dagster import Field, get_dagster_logger, op

from dino.utils.filesystem import find_files_matching_patterns
from dino.utils.splunk import SplunkHEC

# ugly patch for : _csv.Error: field larger than field limit (131072)
# see: https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
csv.field_size_limit(sys.maxsize)

def _fix_nul_bytes(f):
    for line in f.readlines():
        yield line.replace('\0', '')

@op(
    required_resource_keys={"splunk"},
    config_schema={
        "file_names_patterns": Field(
            [str], description="Move files matching a specific pattern"
        ),
        "source": Field(str, description="Source field used by splunk"),
        "sourcetype": Field(str, description="Sourcetype field used by splunk"),
        "encoding": Field(
            str, description="Encoding of the file", default_value="utf-8"
        ),
        "skip": Field(
            bool,
            description="Whether or not to skip execution of this op",
            default_value=False,
        ),
    },
)
def send_csv_files(context, folder: Path):
    logger = get_dagster_logger()
    if context.op_config["skip"]:
        logger.info(f"Skipping execution of send_csv_files for {folder}")
        return
    logger.debug(
        f"Sending csv files matching `{context.op_config['file_names_patterns']}` from `{folder}`"
    )

    for file in find_files_matching_patterns(
        folder, context.op_config["file_names_patterns"]
    ):
        with context.resources.splunk.stream(
            host=str(file.absolute()),
            source=context.op_config["source"],
            sourcetype=context.op_config["sourcetype"],
        ) as hec:
            with open(file, encoding=context.op_config["encoding"]) as csv_file:
                csv_reader = csv.DictReader(_fix_nul_bytes(csv_file))
                for row in csv_reader:
                    hec.send_dict(row)
                    # TODO: remove empty key/values


@op(
    required_resource_keys={"splunk"},
    config_schema={
        "source": Field(str, description="Source field used by splunk"),
        "sourcetype": Field(str, description="Sourcetype used by splunk"),
    },
)
def send_json_file(context, file: Path):
    logger = get_dagster_logger()

    logger.debug(
        f"Sending json file `{file}` to `{context.resources.splunk}` source: {context.op_config['sourcetype']}"
    )

    with context.resources.splunk.stream(
        host=str(file.absolute()),
        source=context.op_config["source"],
        sourcetype=context.op_config["sourcetype"],
    ) as hec:
        with open(file, encoding="utf-8") as json_file:
            for line in json_file.readlines():
                hec.send(line.encode("utf-8") + b"\n")
