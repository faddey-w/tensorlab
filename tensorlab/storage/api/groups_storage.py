from tensorlab.core.groups import GroupsStorage as _BaseGroupsStorage, Group
from tensorlab.storage.db import tables, utils


class GroupsStorage(_BaseGroupsStorage):

    def __init__(self, db):
        self._db = db

    def list(self):
        return utils.read_many(self._db, tables.Groups.select(), self._row_to_group)

    def get(self, group_name):
        return self._row_to_group(utils.read_one(self._db, tables.Groups, name=group_name))

    def save(self, group):
        if group.key:
            dirty = _get_dirty(group)
            if dirty:
                upd_q = tables.Groups.update()\
                    .where(tables.Groups.c.id == group.key['id'])\
                    .values(**dirty)
                self._db.execute(upd_q)
                _update_from_dict(group, dirty)
        else:
            ins_q = tables.Groups.insert().values(name=group.name)
            ret = self._db.execute(ins_q)
            group.key = _group_key_from_row({
                'id': ret.inserted_primary_key,
                'name': group.name,
            })

    def add_or_update_attrs(self, group, attribute, *more_attributes):
        pass

    def delete_attrs(self, group, attribute, *more_attributes):
        pass

    def get_group(self, attribute):
        pass

    def list_models(self, group):
        return []

    def list_attrs(self, group):
        pass

    def delete_with_content(self, group):
        pass

    def _row_to_group(self, row):
        key = _group_key_from_row(row)
        return Group(key, self, **key['orig_fields'])


def _group_args_from_row(row):
    return {'name': row['name']}


def _group_key_from_row(row):
    return {
        'id': row['id'],
        'orig_fields': _group_args_from_row(row)
    }


def _get_dirty(group):
    return {
        field: getattr(group, field)
        for field, orig_value in group.key['orig_fields'].items()
        if orig_value != getattr(group, field)
    }


def _update_from_dict(group, fields):
    group.key['orig_fields'].update(fields)
    for fld, val in fields.items():
        setattr(group, fld, val)
