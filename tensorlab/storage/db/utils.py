import sqlalchemy as sa


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
