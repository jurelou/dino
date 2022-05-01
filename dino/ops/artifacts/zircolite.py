import subprocess
from pathlib import Path

from dagster import Field, get_dagster_logger, op

from dino import layout_manager


@op(
    config_schema={
        "file_extension": Field(
            str, description="Evtx file extension.", default_value="evtx"
        )
    },
)
def process_zircolite(context, folder: Path) -> Path:
    """Runs zircolite against a folder of evtx files."""
    logger = get_dagster_logger()
    output_file = layout_manager.make_temp_dir(folder) / "rules_generic.json"
    logger.info(
        f"Process evtx folder {folder} using file extension {context.op_config['file_extension']}"
    )
    command = [
        "python3",
        "zircolite.py",
        "--fileext",
        context.op_config["file_extension"],
        "--evtx",
        str(folder.absolute()),
        "--ruleset",
        "rules/rules_windows_generic_full.json",
        "--template",
        "templates/exportForSplunk.tmpl",
        "--templateOutput",
        output_file,
    ]
    res = subprocess.run(command, cwd="./external_tools/Zircolite", capture_output=True)
    logger.debug(res.stdout.decode("utf-8", "replace"))
    logger.info(f"Executed `{command}` Return code: {res.returncode}")
    if res.returncode != 0:
        logger.critical(res.stderr.decode("utf-8", "replace"))
        raise Exception("Error while executing zircolite.")
    return output_file
