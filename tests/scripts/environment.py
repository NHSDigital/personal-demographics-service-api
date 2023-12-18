import os
from warnings import warn


class EnvVarWrapper(object):
    """Dictionary-like interface for accessing environment variables.
    Values are lazy-loaded so need not exist when EnvVarWrapper is created.
    If the value points to a file on disk the contents are returned."""

    def __init__(self, **kwargs):
        """Supply keyword arguments specifying environment variables to wrap.
        """
        self._env = kwargs

    def __getitem__(self, key):
        try:
            environment_variable = self._env[key]
            value = os.environ[environment_variable]
        except KeyError:
            warn(f'KeyError occured when attempting to retrieve {key} from environment variables.')
            return None

        if os.path.isfile(value):
            with open(value) as f:
                file_content = f.read()
            if not file_content:
                raise RuntimeError("File appears to be empty")
            return file_content
        else:
            return value

    def contains(self, key: str):
        try:
            _ = self[key]
        except KeyError:
            return False
        return True
