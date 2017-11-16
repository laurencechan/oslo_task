#coding=utf-8
import functools
from oslo_utils import timeutils
from oslo_db import exception as db_exc
from oslo_log import log as logging
from oslo_db import api as oslo_db_api
from oslo_db.sqlalchemy import enginefacade
from oslo_task.db.sqlalchemy import models
from oslo_task._i18n import _, _LI, _LE, _LW
from oslo_task import utils
from oslo_task import exception
import oslo_task.conf

OSLO_CONF = oslo_task.conf.OSLO_CONF

LOG = logging.getLogger(__name__)
#获取上文管理器，与数据库有关的
task_context_manger=enginefacade.transaction_context()

def _get_db_conf(conf_group, connection=None):
    kw = dict(
        connection=connection or conf_group.connection,
        slave_connection=conf_group.slave_connection,
        sqlite_fk=False,
        __autocommit=True,
        expire_on_commit=False,
        mysql_sql_mode=conf_group.mysql_sql_mode,
        idle_timeout=conf_group.idle_timeout,
        connection_debug=conf_group.connection_debug,
        max_pool_size=conf_group.max_pool_size,
        max_overflow=conf_group.max_overflow,
        pool_timeout=conf_group.pool_timeout,
        sqlite_synchronous=conf_group.sqlite_synchronous,
        connection_trace=conf_group.connection_trace,
        max_retries=conf_group.max_retries,
        retry_interval=conf_group.retry_interval)
    return kw

def configure(conf):
    task_context_manger.configure(**_get_db_conf(conf.database))

def get_engine(use_slave=False):
     return task_context_manger.get_legacy_facade().get_engine(use_slave=use_slave)

#以写模式获取数据库会话
def pick_context_manager_writer(f):
    """Decorator to use a writer db context manager.

    The db context manager will be picked from the RequestContext.

    Wrapped function must have a RequestContext in the arguments.
    """
    @functools.wraps(f)
    def wrapped(context, *args, **kwargs):
        ctxt_mgr = task_context_manger
        with ctxt_mgr.writer.using(context):
            return f(context, *args, **kwargs)
    return wrapped

#以读模式获取数据库会话
def pick_context_manager_reader(f):
    """Decorator to use a reader db context manager.

    The db context manager will be picked from the RequestContext.

    Wrapped function must have a RequestContext in the arguments.
    """
    @functools.wraps(f)
    def wrapped(context, *args, **kwargs):
        ctxt_mgr = task_context_manger
        with ctxt_mgr.reader.using(context):
            return f(context, *args, **kwargs)
    return wrapped

@pick_context_manager_reader
def task_get_by_id(context, task_id):
    query_prefix = context.session.query(models.Task)
    query_prefix = query_prefix.filter(models.Task.uuid == task_id)
    result = query_prefix.first()
    if not result:
        raise exception.NotFound(task_id)
    return result

@pick_context_manager_reader
def event_get_by_id(context, event_id):
    query_prefix = context.session.query(models.Event)
    query_prefix = query_prefix.filter(models.Event.uuid == event_id)
    result = query_prefix.first()
    if not result:
        raise exception.NotFound(event_id)
    return result

@oslo_db_api.wrap_db_retry(max_retries=5, retry_on_deadlock=True)
@pick_context_manager_writer
def task_add(context,values):
    task_ref=models.Task()
    values = values.copy()
    if not values.get('uuid'):
        values['uuid'] = utils.make_uuid(context,'task')
    task_ref.update(values)
    try:
        task_ref.save(context.session)
    except db_exc.DBDuplicateEntry as e:
        LOG.error("the error in task create is %s,task_id is %s",str(e),values['uuid'])
        raise exception.CreateFailed(values['uuid'])
    return task_ref

@oslo_db_api.wrap_db_retry(max_retries=5, retry_on_deadlock=True)
@pick_context_manager_writer
def event_add(context,values):
    event_ref = models.Event()
    values = values.copy()
    if not values.get('uuid'):
        values['uuid'] = utils.make_uuid(context, 'event')
    event_ref.update(values)
    try:
        event_ref.save(context.session)
    except db_exc.DBDuplicateEntry as e:
        LOG.error("the error in event create is %s,event_id is %s", str(e), values['uuid'])
        raise exception.CreateFailed(values['uuid'])
    return event_ref

@oslo_db_api.wrap_db_retry(max_retries=5, retry_on_deadlock=True)
@pick_context_manager_writer
def task_update(context,task_id,values):
    task_ref=task_get_by_id(context,task_id)
    values['updated_at']=timeutils.utcnow()
    task_ref.update(values)
    try:
        task_ref.save(context.session)
    except Exception as e:
        msg = (_("There is in task udpate occuring error %(err)s with ID %(id)s") %
               dict(err=str(e), id=task_id))
        LOG.error(msg)
        raise exception.UpdateFailed(task_id)

@oslo_db_api.wrap_db_retry(max_retries=5, retry_on_deadlock=True)
@pick_context_manager_writer
def event_update(context,event_id,values):
    event_ref = event_get_by_id(context, event_id)
    event_ref.update(values)
    try:
        event_ref.save(context.session)
    except Exception as e:
        msg = (_("There is in event udpate occuring error %(err)s with ID %(id)s") %
               dict(err=str(e), id=event_id))
        LOG.error(msg)
        raise exception.UpdateFailed(event_id)

@pick_context_manager_reader
def task_get(context,filters):
    pass

@pick_context_manager_reader
def event_get(context,filters):
    pass
