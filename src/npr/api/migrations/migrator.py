from packaging import version as _v

from npr import __version__


class Migrator:
    versions = {}

    def register(self, version: str):
        def __decorator__(f):
            if version in self.versions:
                raise Exception()

            if _v.parse(version) > _v.parse(__version__):
                raise Exception()

            self.versions[version] = f

            return f

        return __decorator__

    def migrate(self, obj: dict):
        state_version = _v.parse(obj.get("__version__", "0.0.0"))
        for migration_version, migration in self.versions.items():
            if state_version >= _v.parse(migration_version):
                continue

            obj = migration(obj)

        return obj


migrator = Migrator()
