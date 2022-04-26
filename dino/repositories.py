from dagster import repository

from dino.jobs.orc import orc


@repository
def repo_a():
    """Repo A."""
    return [orc]
