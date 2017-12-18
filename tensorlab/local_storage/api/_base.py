import sqlalchemy as sa
from tensorlab.core import groups, models, runs, attributes
from tensorlab.local_storage.db import utils, tables as _t


class LocalStorageBase:
    
    def _get_group_by_id(self, db, group_id):
        row = utils.read_one(db, _t.Groups, id=group_id)
        return self._row_to_group(row)

    def _get_model_by_id(self, db, model_id):
        row = utils.read_one(db, _t.Models, id=model_id)
        return self._row_to_model(row)

    def _row_to_group(self, row):
        key = self._make_group_key(
            row['id'], row['uid'], row['parent_id'], row['name'])
        return groups.Group(key, self, **key['orig_fields'])

    def _make_group_key(self, id, uid, parent_id, name):
        return {'id': id, 'uid': uid, 'parent_id': parent_id,
                'orig_fields': {'name': name}}

    def _row_to_attribute(self, row):
        fields = {
            'name': row['name'],
            'type': row['type'],
            'runtime': row['runtime'],
            'options': row['options'],
            'default': row['default'],
            'nullable': row['nullable'],
        }
        key = self._make_attribute_key(row['id'], row['group_id'], fields)
        return attributes.Attribute(key=key, storage=self, **fields)

    def _make_attribute_key(self, id, group_id, fields):
        return {'id': id, 'group_id': group_id, 'orig_fields': fields}

    def _row_to_model(self, row):
        key = self._make_model_key(**row)
        return models.Model(key, self, name=row['name'])

    def _make_model_key(self, id, uid, group_id, name):
        return {
            'id': id,
            'uid': uid,
            'group_id': group_id,
            'orig_fields': {'name': name}
        }

    def _make_run_key(self, id, uid, model_id, started_at, finished_at):
        return {
            'id': id, 'uid': uid, 'model_id': model_id,
            'orig_fields': {'started_at': started_at, 'finished_at': finished_at}
        }

    def _row_to_run(self, row):
        key = self._make_run_key(**row)
        return runs.Run(key, self, **key['orig_fields'])

    def _fetch_attr_values(self, db, uids, attr_defs, runtime):
        q = _t.AttributeValues.select().where(
            _t.AttributeValues.c.target_uid.in_(uids)
        ).where(
            _t.AttributeValues.c.runtime == sa.true() if runtime else sa.false()
        )
        result = {uid: {} for uid in uids}
        attr_defs = {utils.get_key(a)['id']: a for a in attr_defs}
        for row in db.execute(q):
            attr_def = attr_defs.get(row['attr_id'])
            if attr_def is None:
                continue
            value = attr_def.decode_value(row['value'])
            result[row['uid']][attr_def.name] = value
        for attrs in result.values():
            for attr_def in attr_defs.values():
                if attr_def.name not in attrs:
                    attrs[attr_def.name] = attr_def.get_default()
        return result
