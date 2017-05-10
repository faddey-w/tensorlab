import sqlalchemy as sa
from tensorlab import exceptions
from tensorlab.core.attributeoptions import AttributeType
from tensorlab.core import groups
from tensorlab.storage.db import tables as _t, utils


class GroupsStorage(groups.GroupsStorage):

    def __init__(self, db, storage):
        self._db = db
        self._storage = storage

    def list(self):
        return utils.read_many(self._db, _t.Groups.select(), self._row_to_group)

    def get(self, group_name):
        row = utils.read_one(self._db, _t.Groups, name=group_name)
        if row is None:
            raise exceptions.LookupError("Group named {!r} not found".format(group_name))
        return self._row_to_group(row)

    def save(self, group):
        if group.key:
            dirty = _get_dirty(group)
            if dirty:
                upd_q = _t.Groups.update()\
                    .where(_t.Groups.c.id == group.key['id'])\
                    .values(**dirty)
                self._db.execute(upd_q)
                _update_from_dict(group, dirty)
        else:
            ins_q = _t.Groups.insert().values(name=group.name)
            ret = self._db.execute(ins_q)
            group.key = _group_key_from_row({
                'id': ret.inserted_primary_key[0],
                'name': group.name,
            })

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

    def list_models(self, group):
        return []
        # return self._storage.models.list(group)

    def list_attrs(self, group):
        return utils.read_many(
            self._db,
            _t.Attributes.select().where(_t.Attributes.c.group_id == group.key['id']),
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

    def _row_to_group(self, row):
        key = _group_key_from_row(row)
        return groups.Group(key, self, **key['orig_fields'])

    def _row_to_attr(self, row):
        key = _attr_key_from_row(row)
        return groups.Attribute(key, self, **key['orig_fields'])


def _group_args_from_row(row):
    return {'name': row['name']}


def _group_key_from_row(row):
    return {
        'id': row['id'],
        'orig_fields': _group_args_from_row(row)
    }


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


def _get_dirty(obj):
    return {
        field: getattr(obj, field)
        for field, orig_value in obj.key['orig_fields'].items()
        if orig_value != getattr(obj, field)
    }


def _update_from_dict(group, fields):
    group.key['orig_fields'].update(fields)
    for fld, val in fields.items():
        setattr(group, fld, val)
