"""Collection of ORC jobs"""
from dagster import configured, job, Field, config_mapping

from dino.ops.artifacts.evtx import process_evtx
from dino.ops.artifacts.chainsaw import process_chainsaw
from dino.ops.decompress import decompress_file
from dino.ops.filesystem import find_file, generate_files
from dino.ops.splunk import send_csv_files, send_json_file
from dino.resources.splunk import splunk


@config_mapping(
    config_schema={
        "source_path": Field(str, description="EVTX source path"),
        "splunk": {
            "host": Field(str, description="Splunk hostname", default_value="splunk"),
            "port": Field(int, description="Splunk port", default_value=8089),
            "index": Field(str, description="Splunk index to use"),
            "username": Field(str, description="Splunk username", default_value="dino"),
            "password": Field(str, description="Splunk password", default_value="password")
        },
        "chainsaw": {
            "files_extension": Field(str, description="Evtx files extension (used by chainsaw)", default_value="evtx_data"),
        },
    }
)
def evtx_preset(val):
    return {
        "resources": {
            "splunk": {
                "config": {
                    "host": val["splunk"]["host"],
                    "port": val["splunk"]["port"],
                    "index": val["splunk"]["index"],
                    "password": val["splunk"]["password"],
                    "username": val["splunk"]["username"]
                }
            }
        },
        "ops": {
            "process_chainsaw": {
                "config": {
                    "file_extension": val["chainsaw"]["files_extension"]
                }
            },
            "gather_evtx": {
                "config": {
                    "source_path": val["source_path"]
                }
            },
        }
    }

@job(resource_defs={"splunk": splunk}, config=evtx_preset)
def evtx():
    """Parse evtx files."""

    # CONFIGURE ops
    gather_evtx = generate_files.alias("gather_evtx")

    zircolite_send_file_configured = send_json_file.configured(
        {"source": "zircolite", "sourcetype": "dino:zircolite/json"},
        name="zircolite_send",
    )

    # RUN pipeline

    evtx_files = gather_evtx()
    evtx_files.map(process_chainsaw).map(zircolite_send_file_configured)
    evtx_files.map(process_evtx)