from .. import files, db
from tensorlab import exceptions


class TensorLabStorage:

    def __init__(self, root_dir):
        self._root = root_dir
        self._db = None

    @property
    def is_opened(self):
        return self._db is not None

    @property
    def root_dir(self):
        return self._root

    def Open(self):
        if self.is_opened:
            _error("Storage is already opened")
        if not files.is_storage_exist(self._root):
            _error("Storage files not found at {}", self._root)
        self._do_init()
        return self

    def Create(self):
        if self.is_opened:
            _error("Storage is already opened")
        if files.is_storage_exist(self._root):
            _error("Storage already created at {}", self._root)
        if not files.create_storage_directory(self._root):
            _error("Cannot create storage at {}", self._root)
        self._do_init()
        return self

    def _do_init(self):
        db.connection.init_db(files.get_db_path(self._root))
        self._db = db.connection.get_connection()


def _error(msg, *args, **kwargs):
    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    raise exceptions.StorageInstantiationError(msg)
