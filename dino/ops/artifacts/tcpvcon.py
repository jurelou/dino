import re
from pathlib import Path
from dagster import get_dagster_logger, op

RULE = re.compile(r"\[(?P<proto>.*)\] (?P<process_name>.*)\n\s+PID:\s+(?P<PID>.*)\n\s+State:\s+(?P<state>.*)\n\s+Local:\s+(?P<local_address>.*)\s\s+Remote:\s+(?P<remote_address>.*)")

@op(
    required_resource_keys={"splunk"}
)
def process_tcpvcon(context, file: Path):
    """Parses a TCPVCON result file."""
    logger = get_dagster_logger()
    logger.info(f"Process tcpvcon file {file}")

    with open(file, mode="rb") as f:
        data = f.read().decode("ISO-8859-1")

    with context.resources.splunk.stream(
        sourcetype="dino/json",
        host=str(file.absolute()),
        source="tcpvcon",
    ) as hec:
        for i in re.finditer(RULE, data):
            hec.send_dict(i.groupdict())
