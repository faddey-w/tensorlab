from tensorlab import exceptions
from . import util, base


if False:
    import typing


class Group:
    """
    Groups form a tree in which models can be organized.

    Group fields:
        * name - name given by user, unique for each parent group
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

    def save(self, parent):
        util.check_storage(self)
        self.storage.save(self, parent)

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

    def get(self, group_name):
        """
        :param group_name: fully qualified group name, separated by slashes
        :type group_name: str
        :return: group object with given name or None if not found
        :rtype: Group
        """
        raise NotImplementedError

    def list(self, parent_group, name_pattern=None):
        """
        :param parent_group: if None, lists top level groups
        :type parent_group: typing.Optional[Group]
        :param name_pattern: glob pattern for filtering,
                             supports "*" and "?" special symbols.
        :type name_pattern: str
        :return: list of all (matching) groups
        :rtype: typing.List[Group]
        """
        raise NotImplementedError

    def create(self, group, parent_group):
        """
        Creates a new group within given parent group.
        :type group: Group
        :param parent_group: if None, creates top level group
        :type parent_group: typing.Optional[Group]
        """
        raise NotImplementedError

    def rename(self, group):
        """
        Saves new name for group
        :type group: Group
        """

    def delete_with_content(self, group):
        """
        Deletes the group and all its subgroups and models with their contents.
        :type group: Group
        """
        raise NotImplementedError

    def list_models(self, group, name_pattern=None, predicate=None):
        """
        Lists models within given group, filters results by given
        name pattern on predicate on attributes.
        Non-recursive.

        Pattern syntax - "%" symbol means "any number of characters
                         "?" symbol means "one charanter"
                         other symbols match as is.
        :type group: typing.Optional[Group]
        :type name_pattern: typing.Optional[str]
        :type predicate: typing.Optional[tensorlab.core.attribute_predicates.Expression]
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
