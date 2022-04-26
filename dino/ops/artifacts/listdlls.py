import re
from pathlib import Path
from dagster import get_dagster_logger, op

RULE = re.compile(r"0x(?P<base_address>.*)\s+0x(?P<size>[a-zA-Z0-9_]*)\s+(?P<path>.*)\n\s+Verified:\s+(?P<verified>.*)\n\s+Publisher:\s+(?P<publisher>.*)\s+Description:\s+(?P<description>.*)\n\s+Product:\s+(?P<product>.*)\n\s+Version:\s+(?P<version>.*)\n\s+File version:\s+(?P<file_version>.*)\n\s+Create time:\s+(?P<create_time>.*)")

@op(
    required_resource_keys={"splunk"}
)
def process_listdlls(context, file: Path):
    """Parses a LISTDLLS result file."""
    logger = get_dagster_logger()
    logger.info(f"Process listdlls file {file}")

    with open(file, mode="rb") as f:
        data = f.read().decode("ISO-8859-1")

    with context.resources.splunk.stream(
        sourcetype="dino/json",
        host=str(file.absolute()),
        source="listdlls",
    ) as hec:
        for i in re.finditer(RULE, data):
            item = i.groupdict()
            item["base_address"] = "0x" + item["base_address"]
            item["size"] = "0x" + item["size"]
            for k in item.keys():
                item[k] = item[k].strip()

            hec.send_dict(item)
