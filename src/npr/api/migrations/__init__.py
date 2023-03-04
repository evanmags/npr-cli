import re
from importlib import import_module
from pathlib import Path

from npr.api.migrations.migrator import migrator  # noqa: F401

for file in Path(__file__).parent.iterdir():
    if match := re.match(r"(?P<version>v\d+_\d+_\d+)\.py$", file.name):
        version = match.group("version")
        import_module(f"npr.api.migrations.{version}")
