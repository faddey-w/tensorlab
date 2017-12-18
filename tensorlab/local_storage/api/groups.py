import sqlalchemy as sa
from sqlalchemy import exc as sa_exc
from tensorlab import exceptions
from tensorlab.core.attributeoptions import AttributeType
from tensorlab.core import groups
from tensorlab.local_storage.db import tables as _t, utils
from . import _base


class LocalGroupsStorage(groups.GroupsStorage, _base.LocalStorageBase):

    def __init__(self, db, storage):
        """
        :type storage: tensorlab.local_storage.api.facade.LocalStorage
        """
        self._db = db
        self._storage = storage

        _root = utils.read_one(
            self._db, _t.Groups, _t.Groups.c.id == _t.Groups.c.parent_id)
        if _root is None:
            self._create_root()
        else:
            self._root = self._row_to_group(_root)

    def _create_root(self):
        uid = utils.make_uid()
        root = groups.Group(name='')
        ins_q = _t.Groups.insert().values(
            name=root.name, uid=uid, parent_id=None)
        ret = self._db.execute(ins_q)
        root.key = self._make_group_key(
            ret.inserted_primary_key[0], uid,
            ret.inserted_primary_key[0], root.name,
        )
        upd_q = _t.Groups.update() \
            .where(_t.Groups.c.id == root.key['id']) \
            .values(parent_id=root.key['id'])
        self._db.execute(upd_q)
        self._root = root

    def get_synced(self, group):
        return set(utils.get_synced_fields(group))

    def get_dirty(self, group):
        return set(utils.get_dirty_fields(group))

    def reset(self, group):
        utils.reset_fields(group)

    def create(self, group, parent_group):
        uid = utils.make_uid()
        parent_group = parent_group or self._root
        parent_id = utils.get_key(parent_group)['id']
        ins_q = _t.Groups.insert().values(
            name=group.name, uid=uid, parent_id=parent_id)
        try:
            ret = self._db.execute(ins_q)
        except sa_exc.IntegrityError:
            raise exceptions.InvalidStateError(
                'Cannot create two subgroups with the same name',
                group)
        group.key = self._make_group_key(
            ret.inserted_primary_key[0], uid, parent_id, group.name,
        )
        group.storage = self

    def list(self, parent_group, name_pattern=None):
        q = _t.Groups.select().order_by('id')
        if name_pattern:
            name_pattern = name_pattern.replace('*', '%').replace('?', '_')
            q = q.where(_t.Groups.c.name.like(name_pattern))
        parent_group = parent_group or self._root
        parent_id = utils.get_key(parent_group)['id']
        q = q.where(_t.Groups.c.parent_id == parent_id)
        q = q.where(_t.Groups.c.id != self._root.key['id'])
        return utils.read_many(self._db, q, self._row_to_group)

    def get(self, group_name):
        if group_name is None:
            return self._root
        name_parts = group_name.split('/')
        data = None
        for i, name in enumerate(name_parts):
            data = self._get(name, data)
            if data is None:
                not_found = '/'.join(name_parts[:i+1])
                raise exceptions.LookupError(
                    "Group named {!r} not found".format(not_found))
        return self._row_to_group(data)

    def _get(self, name, parent_key):
        row = utils.read_one(
            self._db, _t.Groups,
            _t.Groups.c.id != self._root.key['id'],
            name=name,
            parent_id=(parent_key or self._root.key)['id']
        )
        return row

    def rename(self, group):
        if utils.get_key(group)['id'] == self._root.key['id']:
            raise exceptions.IllegalArgumentError("Cannot rename root group")
        dirty = utils.get_dirty_fields(group)
        utils.update_obj(self._db, group, _t.Groups, dirty)

    def add_or_update_attrs(self, group, attribute, *more_attributes):
        if not group.key:
            raise exceptions.InvalidStateError("Group is not saved")
        attrs = [attribute, *more_attributes]

        # apply integrity policy:
        if any(a.target == groups.AttributeTarget.Model
               and not a.default and not a.key and not a.nullable
               for a in attrs):
            if self.count_models(group) > 0:
                raise exceptions.IllegalArgumentError(
                    "You try to add new model attributes without "
                    "default value specified while some models already exist")
        if any(a.target == groups.AttributeTarget.Instance
               and not a.default and not a.key and not a.nullable
               for a in attrs):
            if self.count_instances(group) > 0:
                raise exceptions.IllegalArgumentError(
                    "You try to add new instance attributes without "
                    "default value specified while some instances already exist")

        illegal_attrs = [a for a in attrs if a.key and a.key['group_id'] != group.key['id']]
        if illegal_attrs:
            raise exceptions.IllegalArgumentError(
                'These attributes do not belong to group "{}": {}'
                .format(group.name, ', '.join(a.name for a in illegal_attrs)))

        to_insert = []
        allowed_updates = {'default', 'nullable', 'options'}
        for attr in attrs:
            if not attr.key:
                to_insert.append(attr)
                continue
            update_dict = {fld: getattr(attr, fld) for fld in allowed_updates}
            if attr.type == AttributeType.Enum:
                update_dict.pop('options')
            upd_ret = self._db.execute(
                _t.Attributes.update()
                .where(_t.Attributes.c.id == attr.key['id'])
                .values(**update_dict))
            if upd_ret.rowcount == 1:
                attr.key['orig_fields'].update(update_dict)
            else:
                to_insert.append(attr)

        for attr in to_insert:
            data = dict(
                group_id=group.key['id'],
                name=attr.name,
                target=attr.target,
                type=attr.type,
                options=attr.options,
                default=attr.type.encode(attr.default) if attr.default else '',
                nullable=attr.nullable,
            )
            ins_ret = self._db.execute(_t.Attributes.insert().values(**data))
            attr.key = {
                'id': ins_ret.inserted_primary_key[0],
                'group_id': group.key['id'],
                'orig_fields': _attr_args_from_row(data)
            }

    def delete_attrs(self, group, attribute, *more_attributes, ok_if_not_exist=False):
        attrs = [attribute, *more_attributes]
        if any(not a.key for a in attrs) and not ok_if_not_exist:
            raise exceptions.IllegalArgumentError("Some attributes are not exist")
        ids = [a.key['id'] for a in attrs if a.key]
        self._db.execute(_t.Attributes.delete().where(_t.Attributes.c.id.in_(ids)))
        for a in attrs:
            a.key = None

    def get_group(self, attribute):
        if not attribute.key:
            raise exceptions.InvalidStateError("Attribute is not saved")
        group_id = attribute.key['group_id']
        row = utils.read_one(self._db, _t.Groups, id=group_id)
        if row is None:
            raise exceptions.InternalError("Group #{} not found".format(group_id))
        return self._row_to_group(row)

    def list_models(self, group, name_pattern=None, predicate=None):
        return self._storage.models.list(group or self._root,
                                         name_pattern, predicate)

    def list_attrs(self, group, type=None, target=None):
        query = _t.Attributes.select().where(_t.Attributes.c.group_id == group.key['id'])
        if type is not None:
            query = query.where(_t.Attributes.c.type == type)
        if target is not None:
            query = query.where(_t.Attributes.c.target == target)
        return utils.read_many(
            self._db, query,
            self._row_to_attr
        )

    def delete_with_content(self, group):
        if not group.key:
            raise exceptions.InvalidStateError("Group is not saved")
        self._db.execute(_t.Groups.delete().where(_t.Groups.c.id == group.key['id']))

    def n_attribute_usages(self, group, attribute, *more_attributes, ok_if_not_exist=False):
        attrs = [attribute, *more_attributes]
        existing_attrs = [a for a in attrs if a.key]
        if not ok_if_not_exist and len(existing_attrs) != len(attrs):
            raise exceptions.IllegalArgumentError("Some attributes are not exist")
        ids = [a.key['id'] for a in existing_attrs]
        query = sa.select([
            _t.Attributes.c.id,
            sa.func.count(_t.Attributes.c.id)
        ]).select_from(
            _t.Attributes.join(
                _t.AttributeValues,
                _t.AttributeValues.c.attr_id == _t.Attributes.c.id
            )
        )\
            .where(_t.Attributes.c.id.in_(ids))\
            .group_by(_t.Attributes.c.id)
        counts_by_id = dict(list(self._db.execute(query)))
        results = []
        for attr in attrs:
            if attr.key:
                results.append(counts_by_id.get(attr.key['id'], 0))
            else:
                results.append(0)
        return results

    def _row_to_attr(self, row):
        key = _attr_key_from_row(row)
        return groups.Attribute(key, self, **key['orig_fields'])


def _attr_args_from_row(row):
    fielddict = {
        key: row[key]
        for key in ['name', 'target', 'type', 'options', 'default', 'nullable']
    }
    if fielddict['default']:
        fielddict['default'] = fielddict['type'].decode(fielddict['default'])
    return fielddict


def _attr_key_from_row(row):
    return {
        'id': row['id'],
        'group_id': row['group_id'],
        'orig_fields': _attr_args_from_row(row)
    }
