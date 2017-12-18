from tensorlab import exceptions
from tensorlab.core.facade import TensorLabStorage
from .. import files


class LocalStorage(TensorLabStorage):

    def __init__(self, root_dir, user_project, log_stream):
        """
        :type root_dir: str
        :type user_project: tensorlab.core.user_project.UserProject
        """
        self._root = root_dir
        self._project = user_project
        self._is_open = False
        self._impl = None
        self.log_stream = log_stream

    @property
    def is_opened(self):
        return self._is_open

    @property
    def root_dir(self):
        return self._root

    @property
    def project(self):
        """
        :rtype: tensorlab.core.user_project.UserProject
        """
        return self._project

    def Open(self):
        if self.is_opened:
            _error("Storage is already opened")
        if not files.is_storage_exist(self._root):
            _error("Storage files not found at {}", self._root)
        self._is_open = True
        return self

    def Create(self):
        if self.is_opened:
            _error("Storage is already opened")
        if files.is_storage_exist(self._root):
            _error("Storage already created at {}", self._root)
        if not files.create_storage_directory(self._root):
            _error("Cannot create storage at {}", self._root)
        self._is_open = True
        self._get_impl()
        return self

    def _get_impl(self):
        if self._impl is None:
            if not self._is_open:
                raise _error("Storage is not opened")
            self._impl = self._create_impl()
        return self._impl

    def _create_impl(self):
        return DefaultImplementation(self, self._root)


class DefaultImplementation:

    def __init__(self, storage, root_dir):
        from .. import db, files
        from . import groups, models, runs, attributes
        self.db = db.connection.init_db_engine(files.get_db_path(root_dir))
        db.tables.initialize_db(self.db)
        self.groups = groups.LocalGroupsStorage(self.db, storage)
        self.models = models.LocalModelsStorage(self.db, storage, storage.log_stream)
        self.runs = runs.LocalRunsStorage(self.db, storage, storage.log_stream)
        self.attributes = attributes.LocalAttributeStorage(self.db, storage)


def _error(msg, *args, **kwargs):
    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    raise exceptions.StorageInstantiationError(msg)
