import pytest

from npr.api.migrations import migrator
from npr.api.migrations.migrator import MigrationException, Migrator
from npr.api.state import AppState


def test_migrations():
    _stream = dict(
        station="wxxi",
        title="NprNews",
        primary=False,
        href="https://npr.stream",
    )
    v0_0_0 = dict(favorites=[_stream], last_played=_stream.copy())

    migrated = migrator.migrate(v0_0_0)
    AppState._load_dict(migrated)


def test_registration_overwrite():
    m = Migrator()

    m.register("0.0.1")(lambda o: o)

    with pytest.raises(MigrationException):
        m.register("0.0.1")(lambda o: o)


def test_registration_higher_version():
    m = Migrator()

    with pytest.raises(MigrationException):
        m.register("999.999.999")(lambda o: o)
