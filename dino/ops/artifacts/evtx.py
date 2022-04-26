from pathlib import Path

import ujson
from dagster import Field, get_dagster_logger, op
from evtx import PyEvtxParser

from dino.utils.filesystem import find_files_matching_patterns


def flatten_dict(j):
    res = {}

    def flatten(x, key=""):
        if type(x) is dict:
            [flatten(x[a], a) for a in x]
        elif type(x) is list:
            [flatten(x[i], str(i)) for i in range(len(x))]
        else:
            res[key] = x

    flatten(j)
    return res


@op(
    required_resource_keys={"splunk"},
    config_schema={
        "file_names_regex": Field(
            [str],
            description="Evtx file extension.",
            default_value=["*.evtx", "*.evtx_data"],
        ),
    },
)
def process_evtx(context, folder: Path):
    """Runs evtxdump against a folder of evtx files and sends them to splunk."""
    # TODO: do not send events directly to splunk.
    # Since dagster does not allow to return a DynamicOut here, we send logs directly (to not lose performance)
    # TODO: Looping throught each event is is very slow !! maybe use jq or something else
    logger = get_dagster_logger()

    for f in find_files_matching_patterns(
        folder, context.op_config["file_names_regex"]
    ):

        with context.resources.splunk.stream(
            host=str(f.absolute()),
            sourcetype="dino:evtx/json",
            source="evtx",
        ) as hec:

            with open(f, "rb") as raw_evtx:
                parser = PyEvtxParser(raw_evtx)
                for r in parser.records_json():
                    flat_event = flatten_dict(ujson.loads(r["data"]))
                    flat_event["timestamp"] = r["timestamp"]
                    flat_event.pop("xmlns", None)
                    hec.send_dict(flat_event)
