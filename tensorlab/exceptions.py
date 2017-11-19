

class TensorLabError(Exception):

    def __init__(self, message, *args):
        super(TensorLabError, self).__init__(*args)
        self.message = message

    def __str__(self):
        return str(self.message)


class InternalError(TensorLabError):
    pass


class StorageInstantiationError(TensorLabError):
    pass


class InvalidStateError(TensorLabError):
    pass


class LookupError(TensorLabError):
    pass


class IllegalArgumentError(TensorLabError):
    pass
