import pathlib

from pkg_resources import parse_requirements
from setuptools import setup

with pathlib.Path("requirements.txt").open() as requirements_txt:
    requirements = [str(req) for req in parse_requirements(requirements_txt)]

with pathlib.Path("requirements-dev.txt").open() as requirements_txt:
    dev_requirements = [str(req) for req in parse_requirements(requirements_txt)]

setup(
    name="dino",
    version="0.1.0",
    description="all-in-one forensics",
    author="Dino",
    author_email="dino",
    url="https://github.com/jurelou/dino",
    # packages=find_namespace_packages(include=['dino', 'dino.*']),
    entry_points={},
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
    python_requires=">=3.8.*, <4",
)
