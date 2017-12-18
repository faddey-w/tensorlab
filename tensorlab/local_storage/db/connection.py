import sqlalchemy as sa


def init_db_engine(db_path, **kwargs):
    return sa.create_engine('sqlite:///' + db_path, **kwargs)
