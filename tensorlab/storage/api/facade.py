from tensorlab import exceptions
from .. import files


class TensorLabStorage:

    def __init__(self, root_dir):
        self._root = root_dir
        self._is_open = False
        self._db = None
        self._groups = None

    @property
    def is_opened(self):
        return self._is_open

    @property
    def root_dir(self):
        return self._root

    @property
    def groups(self):
        """
        :rtype: tensorlab.storage.api.groups_storage.GroupsStorage
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
            from .. import db
            from .groups_storage import GroupsStorage
            self._db = db.connection.init_db_engine(files.get_db_path(self._root))
            db.tables.initialize_db(self._db)
            self._groups = GroupsStorage(self._db, self)


def _error(msg, *args, **kwargs):
    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    raise exceptions.StorageInstantiationError(msg)
