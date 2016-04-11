from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('nickname', VARCHAR(length=64)),
    Column('avatar', VARCHAR(length=128)),
    Column('email', VARCHAR(length=120)),
    Column('password', VARCHAR(length=128)),
    Column('timestamp', DATETIME),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('nickname', String(length=64)),
    Column('avatar', String(length=128)),
    Column('email', String(length=120)),
    Column('password', String(length=128)),
    Column('regtime', DateTime),
    Column('about_me', String(length=150)),
    Column('last_seen', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['user'].columns['timestamp'].drop()
    post_meta.tables['user'].columns['about_me'].create()
    post_meta.tables['user'].columns['last_seen'].create()
    post_meta.tables['user'].columns['regtime'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['user'].columns['timestamp'].create()
    post_meta.tables['user'].columns['about_me'].drop()
    post_meta.tables['user'].columns['last_seen'].drop()
    post_meta.tables['user'].columns['regtime'].drop()
