from tensorlab.core import base


class Run:

    def __init__(self, key=None, storage=None, *, started_at, finished_at):
        self.key = key
        self.storage = storage
        self.started_at = started_at
        self.finished_at = finished_at

    def __repr__(self):
        return 'Run(started_at={}, finished_at={})'.format(
            self.started_at, self.finished_at)

    def get_fields(self):
        return {'started_at': self.started_at, 'finished_at': self.finished_at}

    def __eq__(self, obj):
        return isinstance(obj, Run) and self.get_fields() == obj.get_fields()


class RunsStorage(base.StorageBase):

    def get(self, model, run_index):
        """:rtype: Run"""
        raise NotImplementedError

    def list(self, model, predicate=None):
        raise NotImplementedError

    def create(self, model, run, attrs):
        raise NotImplementedError

    def set_time(self, run, start_datetime=None, end_datetime=None):
        raise NotImplementedError

    def get_data_path(self, run):
        raise NotImplementedError

    def get_model(self, run):
        raise NotImplementedError

    def get_group(self, run):
        raise NotImplementedError

    def delete(self, run):
        raise NotImplementedError
