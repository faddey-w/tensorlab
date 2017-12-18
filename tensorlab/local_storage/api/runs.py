import time
import sqlalchemy as sa
from tensorlab.core.runs import RunsStorage, Run
from tensorlab import exceptions
from tensorlab.local_storage.db import tables as _t, utils
from tensorlab.local_storage import files
from . import _base


class LocalRunsStorage(RunsStorage, _base.LocalStorageBase):

    def __init__(self, db, storage, log_stream):
        """
        :type storage: tensorlab.local_storage.api.facade.LocalStorage
        """
        self._db = db
        self._storage = storage
        self._log_stream = log_stream

    def get_synced(self, run):
        return set(utils.get_synced_fields(run))

    def get_dirty(self, run):
        return set(utils.get_dirty_fields(run))

    def reset(self, obj):
        utils.reset_fields(obj)

    def create(self, model, run, attrs):
        model_id = utils.get_key(model)['id']
        uid = utils.make_uid()
        run.started_at = time.time()
        q = _t.Runs.insert().values(
            uid=uid,
            started_at=run.started_at,
            finished_at=run.finished_at,
        )
        ret = self._db.execute(q)
        key = self._make_run_key(
            id=ret.inserted_primary_key[0],
            uid=uid, model_id=model_id,
            started_at=run.started_at,
            finished_at=run.finished_at,
        )
        run.key = key
        run.storage = self

        run_data_dir = self.get_data_path(run)
        files.make_dir_writable(run_data_dir)

        self._storage.project.run(
            attributes=attrs,
            model_data=self._storage.models.get_data_path(model),
            run_data=run_data_dir,
            stream=self._log_stream
        )
        self.set_time(run, finished_at=time.time())

    def get(self, model, run_index):
        model_id = utils.get_key(model)['id']

        q = _t.Runs.select().where(
            _t.Runs.c.model_id == model_id
        ).order_by(_t.Runs.c.started_at).limit(1).offset(run_index)
        row = utils.read_one(self._db, q, self._row_to_run)
        return self._row_to_run(row)

    def list(self, model, predicate=None):
        model_id = utils.get_key(model)['id']
        q = _t.Runs.select().where(
            _t.Runs.c.model_id == model_id
        ).order_by(_t.Runs.c.started_at)
        result = utils.read_many(self._db, q, self._row_to_run)
        return result

    def __list(self, group=None, model=None, attrdict=None, fetch_models=False):
        outer_predicates = []
        do_join_models = fetch_models
        if model:
            if not model.key:
                raise exceptions.InvalidStateError("Model is not stored into DB")
            model_id = model.key['id']
            outer_predicates.append(_t.Instances.c.model_id == model_id)
        elif group:
            if not group.key:
                raise exceptions.InvalidStateError("Group is not stored into DB")
            group_id = group.key['id']
            do_join_models = True
            outer_predicates.append(_t.Models.c.group_id == group_id)

        if attrdict:
            # if any(attr.key is None for attr in attrdict.keys()):
            #     raise exceptions.InvalidStateError("Some attributes are not stored into DB")

            av_type_predicate = sa.and_(
                _t.AttributeValues.c.target_uid == _t.Instances.c.uid,
                _t.Attributes.c.target == AttributeTarget.Instance
            )

            if any(attr.target == AttributeTarget.Model
                   for attr in attrdict.keys()):
                do_join_models = True
                av_type_predicate = sa.or_(
                    av_type_predicate,
                    sa.and_(
                        _t.AttributeValues.c.target_uid == _t.Models.c.uid,
                        _t.Attributes.c.target == AttributeTarget.Model
                    )
                )

            inner_predicates = []
            for attr, value in attrdict.items():
                if isinstance(value, (tuple, list, set)):
                    inner_predicate = sa.or_(
                        _t.AttributeValues.c.value ==
                            attr.type.encode(v, attr.options)
                        for v in value
                    )
                else:
                    inner_predicate = (
                        _t.AttributeValues.c.value ==
                            attr.type.encode(value, attr.options)
                    )
                inner_predicates.append(sa.and_(
                    inner_predicate,
                    _t.Attributes.c.name == attr.name
                ))
            outer_predicates.append(
                len(attrdict) == sa.select([
                    sa.func.count()
                ]).select_from(_t.Attributes.join(
                    _t.AttributeValues,
                    _t.AttributeValues.c.attr_id == _t.Attributes.c.id
                )).where(sa.and_(
                    av_type_predicate,
                    sa.or_(*inner_predicates)
                )).as_scalar()
            )

        selectfrom = _t.Instances
        if do_join_models:
            selectfrom = selectfrom.join(
                _t.Models,
                _t.Instances.c.model_id == _t.Models.c.id
            )

        selection = [_t.Instances, _t.Models] if fetch_models else [_t.Instances]
        query = sa.select(selection)\
            .select_from(selectfrom)\
            .where(sa.and_(*outer_predicates))
        # print(query.compile(self._db, compile_kwargs={"literal_binds": True}))

        results = [self._row_to_instance(row) for row in self._db.execute(query)]
        return results

    def set_time(self, run, started_at=None, finished_at=None):
        if started_at is not None:
            run.started_at = started_at
        if finished_at is not None:
            run.finished_at = finished_at
        fields = utils.get_dirty_fields(run)
        utils.update_obj(self._db, run, _t.Runs, fields)

    def get_data_path(self, run):
        return files.get_run_data_dir(self._storage.root_dir, run)

    def get_group(self, run):
        model = self.get_model(run)
        return self._storage.models.get_group(model)

    def get_model(self, run):
        return self._get_model_by_id(self._db, utils.get_key(run)['model_id'])

    def delete(self, run):
        utils.get_key(run)
        q = _t.AttributeValues.delete().where(_t.AttributeValues.c.id.in_(
            _t.AttributeValues.select([_t.AttributeValues.c.id]).join(
                _t.AttributeValues.join(_t.Attributes)
            ).where(
                _t.AttributeValues.c.target_uid == run.key['uid']
            ).where(
                _t.Attributes.c.runtime == sa.true()
            )
        ))
        self._db.execute(q)

        q = _t.Runs.delete().where(id=run.key['id'])
        self._db.execute(q)

        run.key = None
