from tensorlab import exceptions
from .. import files
from ..files.config import Config


class TensorLabStorage:

    def __init__(self, root_dir, implementation=None):
        self._root = root_dir
        self._is_open = False
        self._db = None
        self._config = Config(files.get_config_path(self._root))
        self._config.load()
        self._groups = None
        self._get_implementation = implementation or DefaultImplementation

    @property
    def is_opened(self):
        return self._is_open

    @property
    def root_dir(self):
        return self._root

    @property
    def config(self):
        """
        :rtype: tensorlab.storage.files.Config
        """
        return self._config

    @property
    def groups(self):
        """
        :rtype: tensorlab.core.groups.GroupsStorage
        """
        self._do_init()
        return self._groups

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
        self._do_init()
        return self

    def _do_init(self):
        if self._db is None:
            if not self._is_open:
                raise _error("Storage is not opened")
            impl = self._get_implementation(self, self._root)
            self._db = impl.db
            self._groups = impl.groups_storage


class DefaultImplementation:

    def __init__(self, storage, root_dir):
        from .. import db, files
        from .groups_storage import GroupsStorage
        self.db = db.connection.init_db_engine(files.get_db_path(root_dir))
        db.tables.initialize_db(self.db)
        self.groups_storage = GroupsStorage(self.db, storage)


def _error(msg, *args, **kwargs):
    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    raise exceptions.StorageInstantiationError(msg)
