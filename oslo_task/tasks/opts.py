from oslo_utils import timeutils
from oslo_task import utils
from oslo_task import exception
from oslo_log import log as logging
from oslo_task._i18n import _LE,_LW
LOG = logging.getLogger(__name__)
class TaskOpteration(object):

    @staticmethod
    def do_task_create(context,task_obj,object_id, task_state, task_name, object_name=None, Istask=False):
        task_values = utils.make_initial_task_values(
            context, object_id, object_name,
            task_state, task_name, Istask
        )
        task_obj._context = context
        task_obj.add(task_values)

    @staticmethod
    def do_task_save(context, task_obj,**kwargs):
        update_values = {}
        update_values.update(kwargs)
        if kwargs['state'] in ['success', 'failed', 'error']:
            update_values['finished_at'] = timeutils.utcnow()
        task_id = utils.make_uuid(context, 'task')
        task_obj._context = context
        try:
            task_obj.save(task_id, update_values)
        except exception.NotFound:
            LOG.warning(_LW("can not find taak_id ,id is %s"), task_id)
        except exception.UpdateFailed:
            LOG.error(_LE("update task failed,task_id is %s"), task_id)
        except Exception as e:
            LOG.error(_LE("unknown error in task save,error is %s"), str(e))

    @staticmethod
    def get_task_by_id(context,task_class,task_id):
        return task_class.get_by_task_id(context,task_id)