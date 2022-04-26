from dagster import Field, get_dagster_logger, resource

from dino.utils.splunk import SplunkHEC


@resource(
    config_schema={
        "index": Field(str, description="Splunk index to use"),
        "host": Field(str, description="Splunk host"),
        "port": Field(int, description="Splunk port", default_value=8089),
        "username": Field(str, description="Splunk username"),
        "password": Field(str, description="Splunk password"),
    }
)
def splunk(init_context):
    logger = get_dagster_logger()
    logger.info(f"Using splunk index {init_context.resource_config['index']}")
    return SplunkHEC(
        index=init_context.resource_config["index"],
        host=init_context.resource_config["host"],
        username=init_context.resource_config["username"],
        password=init_context.resource_config["password"],
    )
