import sqlalchemy as sa


_engine = None


def init_db(db_path, **kwargs):
    global _engine
    _engine = sa.create_engine('sqlite:///' + db_path, **kwargs)


def get_connection():
    if _engine is None:
        raise Exception("Database engine is not initialized!")
    return _engine.connect()
