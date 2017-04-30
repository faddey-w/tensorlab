import sqlalchemy as sa


def read_one(db, query, **filters):
    if hasattr(query, 'c'):
        query = query.select()
        if filters:
            query = query.where([
                (getattr(query.c, field) == value)
                for field, value in filters.items()
            ])
    cursor = db.execute(query)
    row = cursor.fetchone()
    cursor.close()
    return row


def read_many(db, query, mapwith=lambda row: row):
    cursor = db.execute(query)
    row = list(map(mapwith, cursor))
    cursor.close()
    return row
