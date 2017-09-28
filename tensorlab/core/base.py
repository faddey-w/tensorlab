
if False:
    import typing


class StorageBase:
    """
    Basic interface of any storage.
    """

    def get_dirty(self, obj):
        """
        :return names of fields whose values that was changed and not yet
                saved to the storage. For non-saved objects returns all fields.
        :rtype: typing.Set[str]
        """
        raise NotImplementedError

    def get_synced(self, obj):
        """
        :return names of fields whose values are the same as
                into the storage, i.e. was not changed.
                For non-saved objects returns empty set.
        :rtype: typing.Set[str]
        """
        raise NotImplementedError

    def reset(self, obj):
        """
        Resets state of the object to what is stored into the storage,
        i.e. cleans "dirty" fields. State after reset is identical to the
        state after last fetching from the storage.
        Note that actual state in the storage may be different.
        :raises tensorlab.exceptions.InvalidStateError
                if the object was not saved yet.
        """
        raise NotImplementedError
