from pathlib import Path
from dagster import get_dagster_logger, op


@op(
    required_resource_keys={"splunk"}
)
def process_psservice(context, file: Path):
    """Parses a PSSERVICE result file."""
    #TODO: refactor this ugly thing !!!!!!!!
    logger = get_dagster_logger()
    logger.info(f"Process psservice file {file}")

    with open(file, mode="rb") as f:
        data = f.read().decode("ISO-8859-1")

    with context.resources.splunk.stream(
        sourcetype="dino/json",
        host=str(file.absolute()),
        source="psservice",
    ) as hec:

        for obj in data.split("SERVICE_NAME"):
            check_dependencies = False
            lines = obj.splitlines()
            if not lines or len(lines) < 4:
                continue
            item = {
                "service_name": lines[0].split(": ")[1],
                "display_name": lines[1].split(": ")[1],
                "description": lines[2]
            }
            for line in lines[3:]:
                line_stripped = line.strip()
                splited_line = [ i for i in line_stripped.split(":") if i]
                if len(splited_line) > 2:
                    continue

                if check_dependencies:
                    part = line_stripped.partition(":")
                    if len(splited_line) == 1 and part[0] == "":
                        item["dependencies"] = item["dependencies"] + ";" + part[2]
                        continue
                    else:
                        check_dependencies = False
                if line_stripped.startswith("TYPE"):
                    item["type"] = splited_line[1] if len(splited_line) > 1 else ""
                elif line_stripped.startswith("START_TYPE"):
                    item["start_type"] = splited_line[1] if len(splited_line) > 1 else ""
                elif line_stripped.startswith("ERROR_CONTROL"):
                    item["error_control"] = splited_line[1] if len(splited_line) > 1 else ""
                elif line_stripped.startswith("BINARY_PATH_NAME"):
                    item["binary_path_name"] = splited_line[1] if len(splited_line) > 1 else ""
                elif line_stripped.startswith("TAG"):
                    item["tag"] = splited_line[1] if len(splited_line) > 1 else ""
                elif line_stripped.startswith("DEPENDENCIES"):
                    item["dependencies"] = splited_line[1] if len(splited_line) > 1 else ""
                    check_dependencies = True
                elif line_stripped.startswith("TAG"):
                    item["tag"] = splited_line[1] if len(splited_line) > 1 else ""
                elif line_stripped.startswith("FAIL_RESET_PERIOD"):
                    item["fail_reset_period"] = splited_line[1] if len(splited_line) > 1 else ""
                elif line_stripped.startswith("SERVICE_START_NAME"):
                    item["service_start_name"] = splited_line[1] if len(splited_line) > 1 else ""
                elif line_stripped.startswith("LOAD_ORDER_GROUP"):
                    item["load_order_group"] = splited_line[1] if len(splited_line) > 1 else ""
            hec.send_dict(item)

