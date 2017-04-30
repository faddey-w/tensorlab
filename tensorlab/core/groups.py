from tensorlab import exceptions
from .attributeoptions import AttributeType, AttributeTarget


class GroupsStorage:

    def new(self, name):
        return Group(None, self, name=name)

    def new_like(self, group):
        return self.new(group.name)

    def list(self):
        raise NotImplementedError

    def get(self, group_name):
        raise NotImplementedError

    def save(self, group):
        raise NotImplementedError

    def delete_with_content(self, group):
        raise NotImplementedError

    def list_models(self, group):
        raise NotImplementedError

    def count_models(self, group):
        return len(self.list_models(group))

    def list_attrs(self, group):
        raise NotImplementedError

    def add_or_update_attrs(self, group, attribute, *more_attributes):
        raise NotImplementedError

    def delete_attrs(self, group, attribute, *more_attributes):
        raise NotImplementedError

    def get_group(self, attribute):
        raise NotImplementedError


class Group:

    def __init__(self, key=None, storage=None, *, name):
        self.key = key
        self.storage = storage  # type: GroupsStorage
        self.name = name

    def __repr__(self):
        return 'Group(name={!r})'.format(self.name)

    def _check_storage(self):
        if not self.storage:
            raise exceptions.InvalidStateError("{} has no storage", repr(self))

    def save(self):
        self._check_storage()
        self.storage.save(self)

    def get_attrs(self):
        self._check_storage()
        return {
            attr.name: attr
            for attr in self.storage.list_attrs(self)
        }

    def update_attrs(self, *attrs, **kwattrs):
        to_delete = set()
        for name, attr in list(kwattrs.items()):
            if attr is None:
                kwattrs.pop(name)
                to_delete.add(name)
        kwattrs = {
            name: attr.derive(name=name) if name != attr.name else attr
            for name, attr in kwattrs.items()
        }
        if to_delete:
            attrs_to_delete = {
                attr.name: attr
                for attr in self.storage.list_attrs(self)
                if attr.name in to_delete
            }
            if len(attrs_to_delete) != len(to_delete):
                raise exceptions.LookupError(
                    "Some attrs that you meant to delete are not exist: {}",
                    ", ".format(to_delete.difference(attrs_to_delete))
                )
            self.storage.delete_attrs(self, *attrs_to_delete.values())
        if attrs or kwattrs:
            self.storage.add_or_update_attrs(self, *attrs, *kwattrs.values())

    def delete(self, force=False):
        if not force:
            n_models = self.storage.count_models(self)
            if n_models > 0:
                raise exceptions.InvalidStateError(
                    "Cannot safely delete group {!r} since it has {} models"
                    .format(self.name, n_models))
        self.storage.delete_with_content(self)


class Attribute:

    def __init__(self, key=None, storage=None, *,
                 name, target, type, options='',
                 default=None, nullable=False):
        self.key = key
        self.storage = storage  # type: GroupsStorage
        self.name = name
        self.target = target  # type: AttributeTarget
        self.type = type  # type: AttributeType
        self.options = options
        self.default = default
        self.nullable = nullable

    def derive(self, **changes):
        kwargs = self.__dict__.copy()
        changes.setdefault('key', None)
        kwargs.update(changes)
        return Attribute(**kwargs)

    def _check_storage(self):
        if not self.storage:
            raise exceptions.InvalidStateError("{} has no storage", repr(self))

    @property
    def group(self):
        self._check_storage()
        return self.storage.get_group(self)
