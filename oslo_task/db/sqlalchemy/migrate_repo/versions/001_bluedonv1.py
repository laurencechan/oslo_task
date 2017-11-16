from migrate.changeset import UniqueConstraint
from oslo_log import log as logging
from sqlalchemy import Boolean, BigInteger, Column, DateTime, Enum, Float
from sqlalchemy import ForeignKey, Index, Integer, MetaData, String, Table
from oslo_task._i18n import _LE

LOG = logging.getLogger(__name__)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    #create tables
    tasks=Table(
        'tasks',meta,
        Column('created_at',DateTime),
        Column('updated_at',DateTime),
        Column('finished_at',DateTime),
        Column('id', Integer, primary_key=True, nullable=False,autoincrement=True),
        Column('uuid',String(length=255),nullable=False),
        Column('user_id',String(length=36)),
        Column('user_ip',String(length=36)),
        Column('task', String(length=255),nullable=False),
        Column('object_id',String(length=255), nullable=False),
        Column('object_name',String(length=127)),
        Column('istask', Boolean),
        Column('state', String(length=36)),
        Column('project_id',String(length=255)),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )
    events=Table(
        'events',meta,
        Column('created_at', DateTime),
        Column('id', Integer, primary_key=True, nullable=False, autoincrement=True),
        Column('uuid', String(length=255), nullable=False),
        Column('event', String(length=255), nullable=False),
        Column('object_id', String(length=255)),
        Column('object_name', String(length=127)),
        Column('user_id', String(length=36)),
        Column('project_id', String(length=255)),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )
    tables=[tasks,events]
    for table in tables:
        try:
            table.create()
        except Exception:
            LOG.info(repr(table))
            LOG.exception(_LE('Exception while creating table.'))
            raise
    #set the task uuid unique
    Index('uuid', tasks.c.uuid, unique=True).create()
    #set the event uuid uniqe
    Index('uuid', events.c.uuid, unique=True).create()
    common_indexes=[]
    task_indexs=[
        Index('task_object_idx', tasks.c.object_id),
        Index('task_user_ip_idx',tasks.c.user_ip),
        Index('task_state_idx', tasks.c.state),
        Index('task_user_idx', tasks.c.user_id),
        Index('task_start_at_finish_at_idx', tasks.c.created_at, tasks.c.finished_at),
        Index('task_project_id_idx', tasks.c.project_id)]
    common_indexes.extend(task_indexs)
    event_indexs=[
        Index('event_object_id_idx', events.c.object_id),
        Index('event_project_id_idx', events.c.project_id),
        Index('event_user_id_idx',events.c.user_id)
    ]
    common_indexes.extend(event_indexs)
    for index in common_indexes:
            index.create(migrate_engine)

    if migrate_engine.name == 'mysql':
        # In Folsom we explicitly converted migrate_version to UTF8.
        migrate_engine.execute(
            'ALTER TABLE migrate_version CONVERT TO CHARACTER SET utf8')
        # Set default DB charset to UTF8.
        migrate_engine.execute(
            'ALTER DATABASE %s DEFAULT CHARACTER SET utf8' %
            migrate_engine.url.database)