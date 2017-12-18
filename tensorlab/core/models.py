from tensorlab import exceptions
from tensorlab.core import base
from . import util


class Model:

    def __init__(self, key=None, storage: 'ModelsStorage'=None, *, name):
        self.key = key
        self.storage = storage
        self.name = name

    def __repr__(self):
        return 'Model(name={!r})'.format(self.name)

    def get_fields(self):
        return {'name': self.name}

    def __eq__(self, obj):
        return isinstance(obj, Model) and self.get_fields() == obj.get_fields()

    def delete(self, force=False):
        util.check_storage(self)
        if not force:
            n_runs = self.storage.count_runs(self)
            if n_runs > 0:
                raise exceptions.InvalidStateError(
                    "Cannot safely delete model {!r} since it was run {} times"
                    .format(self.name, n_runs))
        self.storage.delete_with_content(self)


class ModelsStorage(base.StorageBase):

    def get(self, group, name):
        """:rtype: Model"""
        raise NotImplementedError

    def list(self, group, name_pattern=None, predicate=None):
        raise NotImplementedError

    def create(self, model, group, attrs):
        raise NotImplementedError

    def rename(self, model):
        raise NotImplementedError

    def get_group(self, model):
        raise NotImplementedError

    def get_data_path(self, model):
        raise NotImplementedError

    def list_runs(self, model, predicate=None):
        raise NotImplementedError

    def count_runs(self, model):
        return len(self.list_runs(model))

    def get_attrs(self, model):
        raise NotImplementedError

    def delete_with_content(self, model):
        raise NotImplementedError
