import sqlalchemy as sa
from tensorlab import exceptions
from tensorlab.core import models, groups
from tensorlab.local_storage.db import tables as _t, utils
from tensorlab.local_storage import files
from . import _base


class LocalModelsStorage(models.ModelsStorage, _base.LocalStorageBase):

    def __init__(self, db, storage, log_stream):
        """
        :type storage: tensorlab.local_storage.api.facade.LocalStorage
        """
        self._db = db
        self._storage = storage
        self._log_stream = log_stream

    def get_synced(self, model):
        return set(utils.get_synced_fields(model))

    def get_dirty(self, model):
        return set(utils.get_dirty_fields(model))

    def reset(self, model):
        utils.reset_fields(model)

    def get(self, group, name):
        if group is None:
            group = self._storage.groups.get(None)
        if isinstance(group, str):
            group = self._storage.groups.get(group)
        if not isinstance(group, groups.Group):
            raise TypeError('Argument "group" should be name or Group instance')
        query = _select_by_group(_t.Models.select(), group)
        return self._row_to_model(utils.read_one(self._db, query))

    def create(self, model, group, attrs):
        if group is None:
            group = self._storage.groups.get(None)
        utils.get_key(group)
        attr_data = self._prepare_attrs(model, attrs, group)

        uid = utils.make_uid()
        ret = self._db.execute(_t.Models.insert().values(
            uid=uid, name=model.name,
            group_id=group.key['id']
        ))
        model.key = self._make_model_key(
            ret.inserted_primary_key[0],
            uid, group.key['id'], model.name)
        model.storage = self

        self._save_attrs(model, attr_data)

        model_path = files.get_model_data_dir(self._storage.root_dir, model)
        files.make_dir_writable(model_path)
        self._storage.project.build(attrs, model_path, self._log_stream)

    def get_data_path(self, model):
        utils.get_key(model)
        return files.get_model_data_dir(self._storage.root_dir, model)

    def list(self, group, name_pattern=None, predicate=None):
        if group is None:
            group = self._storage.groups.get(None)
        query = _select_by_group(_t.Models.select(), group)
        if name_pattern is not None:
            name_pattern = name_pattern.replace('*', '%').replace('?', '_')
            query = query.where(_t.Models.c.name.like(name_pattern))
        if False:
            existing_attrs = group.get_attrs()
            attr_pairs = []
            for key, val in attrs.items():
                if key not in existing_attrs:
                    raise exceptions.LookupError('Attribute "{}" does not exist'.format(key))
                attr_pairs.append((existing_attrs[key], val))
            predicate, has_targets = utils.build_attr_predicate(attr_pairs)
            if (has_targets[groups.AttributeTarget.Instance]
                    or has_targets[groups.AttributeTarget.Run]):
                raise exceptions.IllegalArgumentError("Only model attributes are allowed")
            query = query.where(predicate)

        return utils.read_many(self._db, query, self._row_to_model)

    def rename(self, model):
        utils.get_key(model)
        dirty = utils.get_dirty_fields(model)
        utils.update_obj(self._db, model, _t.Models, dirty)

    def get_attrs(self, model):
        return self._storage.attributes.get_attr_values_for_model(model)

    def get_group(self, model):
        _check_key(model)
        return self._row_to_group(
            utils.read_one(self._db, _t.Groups.select(), id=model.key['group_id'])
        )

    def list_runs(self, model, predicate=None):
        return self._storage.runs.list(model, predicate)

    def delete_with_content(self, model):
        pass

    def _prepare_attrs(self, model, attrs, group=None):
        group = group or self.get_group(model)

        attr_defs = self._storage.attributes.list_effective(group)
        attr_defs = {a.name: a for a in attr_defs if not a.runtime}

        return [
            {
                'value': attrdef.type.encode(attrs[name], attrdef.options),
                'attr_id': attrdef.key['id']
            }
            for name, attrdef in attr_defs.items()
        ]

    def _save_attrs(self, model, attr_data):
        for item in attr_data:
            item['target_uid'] = model.key['uid']
        self._db.execute(_t.AttributeValues.insert().values(attr_data))

    def _row_to_model(self, row):
        key = _model_key(row)
        model = self.new(**key['orig_fields'])
        model.key = key
        return model

    def _row_to_attr(self, row):
        key = _attr_key_from_row(row)
        return groups.Attribute(key, self, **key['orig_fields'])


def _model_key(row):
    return {
        'id': row['id'],
        'uid': row['uid'],
        'group_id': row['group_id'],
        'orig_fields': _model_args(row),
    }


_UPDATE_ALLOWED = ()


def _model_args(row):
    return {'name': row['name'], 'typeinfo': row['typeinfo']}


def _model_to_row(model, with_uid, onlydirty=False, group_id=None):
    if model.key and onlydirty:
        orig = model.key['orig_fields']
        row = {}
        for fld in _UPDATE_ALLOWED:
            if orig[fld] != getattr(model, fld):
                row[fld] = getattr(model, fld)
    else:
        row = {fld: getattr(model, fld) for fld in _UPDATE_ALLOWED}
    if with_uid:
        row['uid'] = model.key['uid'] if model.key else utils.make_uid()
    if group_id is not None:
        row['group_id'] = group_id
    return row


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


def _check_key(obj):
    if not obj.key:
        raise exceptions.InvalidStateError(
            "{!r} is not saved into DB".format(obj))


def _select_by_group(query, group, do_join=True):
    if isinstance(group, str):
        if do_join:
            query = query.join(_t.Groups, _t.Groups.c.id == _t.Models.c.group_id)
        query = query.where(_t.Groups.c.name == group)
    else:
        _check_key(group)
        query = query.where(_t.Groups.c.name == group.key['id'])
    return query
