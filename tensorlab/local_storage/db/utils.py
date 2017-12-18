import uuid
import importlib
import sqlalchemy as sa
from tensorlab import exceptions
from tensorlab.local_storage.db import tables as _t


def read_one(db, query, *filters, **kwfilters):
    if isinstance(query, sa.Table):
        table = query
        query = query.select()
        if filters or kwfilters:
            query = query.where(conjunction(
                table, *filters, **kwfilters
            ))
    cursor = db.execute(query)
    row = cursor.fetchone()
    cursor.close()
    return row


def read_many(db, query, mapwith=lambda row: row):
    cursor = db.execute(query)
    row = list(map(mapwith, cursor))
    cursor.close()
    return row


def conjunction(table, *filters, **kwfilters):
    if not filters and not kwfilters:
        return None
    return sa.sql.and_(
        *filters,
        *((getattr(table.c, key) == val)
          for key, val in kwfilters.items())
    )


def aggregate(db, table, func, *filters, **kwfilters):
    q = table.select([func])
    if filters or kwfilters:
        q = q.where(conjunction(table, *filters, **kwfilters))
    ret = db.execute(q)
    import pdb; pdb.set_trace()


def update_obj(db, obj, table, fields):
    if fields:
        new_values = {k: getattr(obj, k) for k in fields}
        upd_q = table.update() \
            .where(table.c.id == obj.key['id']) \
            .values(**new_values)
        db.execute(upd_q)
        fill_from_dict(obj, new_values)


def make_uid():
    return uuid.uuid4().hex[:16]


def get_table_for_target(attr_target):
    if attr_target == AttributeTarget.Run:
        return _t.Runs
    if attr_target == AttributeTarget.Instance:
        return _t.Instances
    if attr_target == AttributeTarget.Model:
        return _t.Models


def build_attr_predicate(attr_pairs):
    attrs, values = zip(*attr_pairs)

    has_targets = {}
    type_predicate = []
    for target in AttributeTarget:
        has_such_targets = any(a.target == target for a in attrs)
        has_targets[target] = has_such_targets
        if has_such_targets:
            type_predicate.append(sa.and_(
                _t.AttributeValues.c.target_uid == get_table_for_target(target).c.uid,
                _t.Attributes.c.target == target
            ))
    type_predicate = sa.or_(*type_predicate)

    value_predicate = []
    for attr, value in attr_pairs:
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
        value_predicate.append(sa.and_(
            inner_predicate,
            _t.Attributes.c.name == attr.name
        ))
    value_predicate = sa.or_(*value_predicate)

    predicate = len(attr_pairs) == sa.select([
        sa.func.count()
    ]).select_from(_t.Attributes.join(
        _t.AttributeValues,
        _t.AttributeValues.c.attr_id == _t.Attributes.c.id
    )).where(sa.and_(
        type_predicate,
        value_predicate
    )).as_scalar()

    return predicate, has_targets


def import_by_spec(import_spec):
    import_spec = import_spec.split(':')
    if len(import_spec) not in (1, 2):
        raise exceptions.IllegalArgumentError("Incorrect spec format")
    import_path = import_spec[0]
    attr_path = (
        import_spec[1].split('.')
        if len(import_spec) == 2
        else []
    )

    try:
        result = importlib.import_module(import_path)

        for attr in attr_path:
            result = getattr(result, attr)
    except (ImportError, AttributeError) as exc:
        raise exceptions.IllegalArgumentError("Cannot import: "+repr(exc))

    return result


def get_synced_fields(obj):
    result = {}
    if obj.key:
        for attr, val in obj.key['orig_fields'].items():
            if val == getattr(obj, attr):
                result[attr] = val
    return result


def get_dirty_fields(obj):
    result = {}
    if obj.key:
        for attr, val in obj.key['orig_fields'].items():
            if val != getattr(obj, attr):
                result[attr] = val
    return result


def reset_fields(obj):
    for attr, val in obj.key['orig_fields'].items():
        setattr(obj, attr, val)


def fill_from_dict(obj, fields):
    obj.key['orig_fields'].update(fields)
    for fld, val in fields.items():
        setattr(obj, fld, val)


def get_key(obj):
    if obj.key is None:
        raise exceptions.InvalidStateError("{!r} does not saved into DB"
                                           .format(obj))
    return obj.key
