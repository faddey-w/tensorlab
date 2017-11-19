from tensorlab import exceptions
from . import util, base


if False:
    import typing


class Group:
    """
    Group represents a development direction of the user's project:
    it may contain different models that implement some module or do some task.

    Group fields:
        * name - unique name given by user
    """

    def __init__(self, key=None, storage=None, *, name):
        """
        :type name: str
        """
        self.key = key
        self.storage = storage  # type: GroupsStorage
        self.name = name

    def __repr__(self):
        return 'Group(name={!r})'.format(self.name)

    def get_fields(self):
        return {'name': self.name}

    def __eq__(self, other):
        if not isinstance(other, Group):
            return False
        return self.get_fields() == other.get_fields()

    def save(self):
        util.check_storage(self)
        self.storage.save(self)

    def delete(self, force=False):
        util.check_storage(self)
        if not force:
            n_models = self.storage.count_models(self)
            if n_models > 0:
                raise exceptions.InvalidStateError(
                    "Cannot safely delete group {!r} since it has {} models"
                    .format(self.name, n_models))
        self.storage.delete_with_content(self)


class GroupsStorage(base.StorageBase):

    def list(self, name_pattern=None):
        """
        :param name_pattern: glob pattern for filtering,
                             supports "*" and "?" special symbols.
        :type name_pattern: str
        :return: list of all (matching) groups
        :rtype: typing.List[Group]
        """
        raise NotImplementedError

    def get(self, group_name):
        """
        :type group_name: str
        :return: group object with given name or None if not found
        :rtype: Group
        """
        raise NotImplementedError

    def save(self, group):
        """
        Saves a new group or updates the name for existing group.
        :type group: Group
        """
        raise NotImplementedError

    def delete_with_content(self, group):
        """
        Deletes the group and all its models with their contents.
        :type group: Group
        """
        raise NotImplementedError

    def list_models(self, group, name_pattern=None):
        """
        Lists models within given model, filters results if pattern is given.
        Pattern syntax - "%" symbol means "any number of characters
                         "?" symbol means "one charanter"
                         other symbols match as is.
        :type group: Group
        :type name_pattern: typing.Optional[str]
        :rtype typing.List[tensorlab.core.models.Model]
        """
        raise NotImplementedError

    def count_models(self, group):
        """
        :type group: Group
        :returns amount of models within given group
        :rtype int
        """
        return len(self.list_models(group))

    def count_instances(self, group):
        """
        :type group: Group
        :returns amount of instances within given group
        :rtype int
        """
        return sum(
            model.count_instances()
            for model in self.list_models(group)
        )

    def count_runs(self, group):
        """
        :type group: Group
        :returns amount of runs within given group
        :rtype int
        """
        return sum(
            model.count_runs()
            for model in self.list_models(group)
        )
