from dagster import repository

from dino.jobs.orc import orc
from dino.jobs.evtx import evtx

@repository
def main_repository():
    """main repository."""
    return [orc, evtx]
