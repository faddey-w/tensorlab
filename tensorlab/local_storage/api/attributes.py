import sqlalchemy as sa
from sqlalchemy import func as sa_func, exc as sa_exc
from tensorlab import exceptions
from tensorlab.core.attributes import AttributeStorage, Attribute
from tensorlab.core.attributeoptions import AttributeType
from tensorlab.local_storage.db import utils, tables as _t
from . import _base


class LocalAttributeStorage(AttributeStorage, _base.LocalStorageBase):

    def __init__(self, db, storage):
        """
        :type storage: tensorlab.local_storage.api.facade.LocalStorage
        """
        self._db = db
        self._storage = storage

    def get_synced(self, attribute):
        return set(utils.get_synced_fields(attribute))

    def get_dirty(self, attribute):
        return set(utils.get_dirty_fields(attribute))

    def reset(self, attribute):
        utils.reset_fields(attribute)

    def create(self, attribute, group):
        if group is None:
            group = self._storage.groups.get(None)
        group_id = utils.get_key(group)['id']
        if attribute.nullable:
            overridden = self._find_in_parent(attribute.name, group_id)
            if overridden is not None and not overridden.nullable:
                raise exceptions.IllegalArgumentError(
                    'Cannot override non-nullable attribute as nullable '
                    'as it violates integrity rules', attribute, overridden
                )
        ins_q = _t.Attributes.insert().values(
            group_id=group_id,
            name=attribute.name,
            type=attribute.type,
            options=attribute.options,
            default=attribute.type.encode(attribute.default, attribute.options),
            nullable=attribute.nullable,
            runtime=attribute.runtime,
        )
        try:
            ret = self._db.execute(ins_q)
        except sa_exc.IntegrityError:
            raise exceptions.InvalidStateError(
                'Cannot create two attributes with the same name',
                attribute)
        attribute.key = self._make_attribute_key(
            ret.inserted_primary_key[0], group_id, attribute.get_fields(),
        )
        attribute.storage = self

    def update(self, attribute):
        dirty = utils.get_dirty_fields(attribute)
        if set(dirty).intersection({'name', 'type', 'runtime'}):
            raise exceptions.IllegalArgumentError(
                'Fields "name", "type", and "runtime" cannot be updated',
                attribute)
        if attribute.type == AttributeType.Enum and 'options' in dirty:
            prev_choices = set(dirty['options'].split(';'))
            next_choices = set(attribute.options.split(';'))
            removed = list(prev_choices - next_choices)
            usages_found = utils.aggregate(
                self._db, _t.AttributeValues, sa_func.exists(),
                _t.AttributeValues.c.value.in_(removed),
                attr_id=attribute.key['id'],
            )
            if usages_found:
                raise exceptions.IllegalArgumentError(
                    'Cannot drop enum choices when used',
                    attribute, removed)
        if 'nullable' in dirty and not attribute.nullable:
            target_table = _t.Runs if attribute.runtime else _t.Models
            q = sa.select([sa_func.exists()]).select_from(
                target_table.join(
                    _t.AttributeValues,
                    target_table.c.uid == _t.AttributeValues.c.target_uid
                ).join(
                    _t.Attributes,
                    _t.AttributeValues.c.attr_id == _t.Attributes.c.id
                )
            )
            ret = self._db.execute(q)
            import pdb; pdb.set_trace()
        utils.update_obj(self._db, attribute, _t.Attributes, dirty)

    def list(self, group):
        if group is None:
            group = self._storage.groups.get(None)
        return self._list_by_id(utils.get_key(group)['id'])

    def list_effective(self, group):
        if group is None:
            group = self._storage.groups.get(None)
        return self._list_effective_by_id(utils.get_key(group)['id'])

    def _list_by_id(self, group_id, name=None):
        filters = {'group_id': group_id}
        if name is not None:
            filters['name'] = name
        q = _t.Attributes.select().where(
            utils.conjunction(_t.Attributes, **filters))
        return utils.read_many(self._db, q, self._row_to_attribute)

    def _list_effective_by_id(self, group_id):
        result_dict = {}
        while True:
            attrs = self._list_by_id(group_id)
            for a in attrs:
                result_dict.setdefault(a.name, a)
            parent_id = self._get_group_by_id(self._db, group_id).key['parent_id']
            if parent_id == group_id:
                break
            group_id = parent_id
        return list(result_dict.values())

    def _find_in_parent(self, name, group_id):
        while True:
            parent_id = self._get_group_by_id(self._db, group_id).key['parent_id']
            if parent_id == group_id:
                break
            group_id = parent_id
            result = self._list_by_id(group_id, name)
            if result:
                return result[0]

    def get_attr_values_for_model(self, model):
        utils.get_key(model)
        if 'cached_attrs' not in model.key:
            attr_defs = self._list_effective_by_id(model.key['group_id'])
            attr_defs = [a for a in attr_defs if not a.runtime]
            attrs = self._fetch_attr_values(
                self._db,
                [model.key['uid']],
                attr_defs,
                runtime=False
            )
            model.key['cached_attrs'] = attrs[model.key['uid']]
        return model.key['cached_attrs'].copy()

    def get_attr_values_for_run(self, run):
        utils.get_key(run)
        if 'cached_attrs' not in run.key:
            model = self._storage.runs.get_model(run)
            attr_defs = self._list_effective_by_id(model.key['group_id'])
            attr_defs = [a for a in attr_defs if a.runtime]
            attrs = self._fetch_attr_values(
                self._db,
                [run.key['uid']],
                attr_defs,
                runtime=True
            )
            run.key['cached_attrs'] = attrs[run.key['uid']]
        return run.key['cached_attrs'].copy()

    def get_defining_group(self, attribute):
        grp_id = utils.get_key(attribute)['group_id']
        return self._get_group_by_id(self._db, grp_id)

    def usage_stats(self, attribute):
        attr_id = utils.get_key(attribute)['id']

        q = _t.AttributeValues.select([sa_func.count()]).where(
            _t.AttributeValues.c.attr_id == attr_id
        )
        ret = self._db.execute(q)
        import pdb; pdb.set_trace()

    def delete_with_values(self, attribute):
        q = _t.Attributes.delete().where(
            _t.Attributes.c.id == utils.get_key(attribute)['id'])
        self._db.execute(q)
