import base64
from pathlib import Path

from dagster import Field, get_dagster_logger, op
from Registry import Registry

#from dino.utils.filesystem import find_files_matching_patterns


def parse_registry_hive(hec, key):
    logger = get_dagster_logger()

    for v in key.values():
        try:
            entry = {
                "key_name": key.name(),
                "key": key.path(),
                "timestamp": key.timestamp().isoformat(),
                "value_name": v.name(),
                "value": v.value(),
                "value_type": v.value_type_str(),
            }
            if entry["value_type"] == "RegFileTime":
                entry["value"] = entry["value"].isoformat()
            elif entry["value_type"] == "RegBin":
                entry["value_type"] = f"RegBin (base64 encoded)"
                entry["value"] = base64.b64encode(entry["value"]).decode("ISO-8859-1")
            elif entry["value_type"] == "RegMultiSZ":
                _tmp_value = ""
                for i in entry["value"]:
                    if isinstance(i, bytes):
                        _tmp_value = _tmp_value + i.decode("ISO-8859-1")
                    else:
                        _tmp_value = _tmp_value + i
                entry["value"] = _tmp_value

            elif isinstance(entry["value"], bytes):
                entry["value_type"] = f"{entry['value_type']} (base64 encoded)"
                entry["value"] = base64.b64encode(entry["value"]).decode("ISO-8859-1")

            hec.send_dict(entry)
        except Exception as err:
            # logger.critical(f"Error while parsing key {key.name()} of type {v.value_type_str()}: {err}")
            ...
    for subkey in key.subkeys():
        parse_registry_hive(hec, subkey)


@op(
    required_resource_keys={"splunk"},
    config_schema={
        "source": Field(
            str, description="Source registry key (SAM, Security, User, ...)"
        ),
    },
)
def process_registry(context, hive_path: Path):
    """Parses registry hives against a folder of files."""
    logger = get_dagster_logger()
    logger.info(
        f"Process registry hive `{hive_path}` ({context.op_config['source']})"
    )

    # for f in find_files_matching_patterns(
    #     folder, context.op_config["file_names_patterns"]
    # ):
    #     logger.debug(f"Found hive {f.absolute()}")
    reg = Registry.Registry(str(hive_path.absolute()))
    with context.resources.splunk.stream(
        sourcetype="dino:registry/json",
        host=str(hive_path.absolute()),
        source=context.op_config["source"],
    ) as hec:
        parse_registry_hive(hec, reg.root())
