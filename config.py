import os


class ConfigException(Exception):
    """Raised when they config variable requested is not found
       in either the `cfg` dict of config.py or
       in `os.environ` (environment variables)."""

    def __init__(self, key):
        super(self, "Config var {} not found.".format(key))

cfg = {
    "D2_API_KEY": None,
    "DISCORD_KEY": None,
    "DISCORD_CHANNEL_ID": None,
}


def get(key):
    if key in os.environ:
        return os.environ[key]
    elif cfg.get(key) is not None:
        return cfg[key]
    else:
        raise ConfigException(key)
