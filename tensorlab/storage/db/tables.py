import sqlalchemy as sa
from tensorlab.core.attributeoptions import AttributeType, AttributeTarget


_metadata = sa.MetaData()


Groups = sa.Table(
    'Groups', _metadata,

    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(60), unique=True),
)


Models = sa.Table(
    'Models', _metadata,

    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('uid', sa.String(16), unique=True),
    sa.Column('group_id', sa.ForeignKey('Groups.id')),
    sa.Column('name', sa.String(60)),
    sa.Column('type_info', sa.String(60)),

    sa.UniqueConstraint('group_id', 'name'),
)


Instances = sa.Table(
    'Instances', _metadata,

    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('uid', sa.String(16), unique=True),
    sa.Column('model_id', sa.ForeignKey('Models.id')),
    sa.Column('name', sa.String(60)),

    sa.UniqueConstraint('model_id', 'name'),
)


Runs = sa.Table(
    'Runs', _metadata,

    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('uid', sa.String(16), unique=True),
    sa.Column('instance_id', sa.ForeignKey('Instances.id')),
    sa.Column('start_dt', sa.DateTime),
    sa.Column('end_dt', sa.DateTime),
)


Attributes = sa.Table(
    'Attributes', _metadata,

    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('group_id', sa.ForeignKey('Groups.id')),
    sa.Column('name', sa.String(60)),
    sa.Column('target', sa.Enum(AttributeTarget)),
    sa.Column('type', sa.Enum(AttributeType)),
    sa.Column('options', sa.String(200)),
    sa.Column('default', sa.String(60)),
    sa.Column('nullable', sa.Boolean),

    sa.UniqueConstraint('group_id', 'name'),
)


AttributeValues = sa.Table(
    'AttributeValues', _metadata,

    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('target_uid', sa.String(16)),
    sa.Column('attr_id', sa.ForeignKey('Attributes.id')),
    sa.Column('value', sa.String(60)),

    sa.UniqueConstraint('target_uid', 'attr_id'),
)


def initialize_db(connection):
    _metadata.create_all(bind=connection)
