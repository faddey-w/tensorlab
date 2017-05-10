import os
import json
import collections
from tensorlab import exceptions


class Config:

    _FIELDS = (
        'projecthook',
    )

    def __init__(self, config_path):
        self._path = config_path
        self._config = {}

    def load(self):
        if os.path.exists(self._path):
            with open(self._path) as f:
                config = json.load(f)
        else:
            config = {}
        for field in self._FIELDS:
            self._config[field] = config.get(field, None)

    def save(self):
        # put the config into an OrderedDict
        # to preserve ordering like in _FIELDS
        ordered_config = collections.OrderedDict()
        for field in self._FIELDS:
            ordered_config[field] = self._config[field]

        with open(self._path, 'w') as f:
            json.dump(ordered_config, f, indent=4)

    def get_fields(self):
        return self._FIELDS

    def __getitem__(self, item):
        if item not in self._FIELDS:
            raise exceptions.IllegalArgumentError(
                "Wrong config key: "+item)
        return self._config[item]

    def __setitem__(self, key, value):
        if key not in self._FIELDS:
            raise exceptions.IllegalArgumentError(
                "Wrong config key: "+key)
        self._config[key] = value
