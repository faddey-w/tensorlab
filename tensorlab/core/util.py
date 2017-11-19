from tensorlab import exceptions


def check_storage(obj):
    if obj.storage is None:
        raise exceptions.InvalidStateError("{!r} has no storage".format(obj))

