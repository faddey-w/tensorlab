

class TensorLabError(Exception):

    def __init__(self, message, *args):
        super(TensorLabError, self).__init__(message, *args)
        self.message = message


class StorageInstantiationError(TensorLabError):
    pass


class InvalidStateError(TensorLabError):
    pass


class LookupError(TensorLabError):
    pass
