import subprocess
from pathlib import Path
import ujson
from dagster import Field, get_dagster_logger, op
import shutil

from dino import layout_manager


@op(
    required_resource_keys={"splunk"},
    config_schema={
        "file_names_patterns": Field(
            [str], description="Evtx file extension.", default_value=["*.evtx", "*.evtx_data"]
        )
    },
)
def process_chainsaw(context, folder: Path):
    """Runs chainsaw against a folder of evtx files."""
    logger = get_dagster_logger()

    evtx_files = folder / "evtx"
    temp_folder = layout_manager.make_temp_dir(evtx_files)

    logger.info(
        f"Process evtx folder {folder} using file extension {context.op_config['file_names_patterns']} using temp folder {temp_folder}"
    )

    for pattern in context.op_config["file_names_patterns"]:
        for evtx_file in evtx_files.rglob(pattern):
            shutil.copy(evtx_file, temp_folder / f"{evtx_file.stem}.evtx")
    
    command = [
        "./chainsaw", "hunt",
        "--rules", "./sigma_rules",
        "--mapping", "./mapping_files/sigma-mapping.yml",
        "--json", "--quiet",
        str(temp_folder.absolute())
    ]
    res = subprocess.run(command, cwd="./external_tools/chainsaw", capture_output=True, text=True)
    logger.info(f"Executed `{command}` Return code: {res.returncode}")
    if res.returncode != 0:
        logger.critical(res.stderr)
        raise Exception("Error while executing zircolite.")
    logger.debug(f"Stderr: {res.stderr}")

    try:
        json_matches = ujson.loads(res.stdout)
    except Exception as err:
        logger.critical(f"Error while loading json matches: {err}")
    

    with context.resources.splunk.stream(
        sourcetype="dino/json",
        host=str(folder.absolute()),
        source="chainsaw",
    ) as hec:
        for match in json_matches:
            hec.send_dict(match)
