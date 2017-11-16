from functools import wraps
from oslo_utils import excutils
from oslo_log import log as logging
from oslo_task._i18n import _LE,_LW
from oslo_task import utils
from oslo_task.tasks import opts as taskopts
from oslo_task import exception
from oslo_task.tasks import glancetask
LOG = logging.getLogger(__name__)

glanceobject=glancetask.GlanceTask
def glancetaskcreate(task_name,IsTask=False):
    def wrap_task(f):
        @wraps(f)
        def taskcreate(self,req,*args,**kwargs):
            task_state='start'
            key_args,newcontext=utils.get_glance_req_args(f,self,req,*args,**kwargs)
            object_id=getattr(key_args,'image_id',None)
            try:
                taskopts.TaskOpteration.do_task_create(newcontext,glanceobject(),
                                                       object_id, task_state,task_name,None,IsTask)
            except exception.CreateFailed:
                LOG.warning(_LW("create a task failed"))
            try:
                return f(self,req,*args,**kwargs)
            except Exception:
                with excutils.save_and_reraise_exception():
                    task_state='failed'
                    taskopts.TaskOpteration.do_task_save(newcontext,glanceobject(),
                                                         state=task_state,object_id=object_id)
            finally:
                if task_state not in ['error','failed']:
                    task_state='success'
                    taskopts.TaskOpteration.do_task_save(newcontext,glanceobject(),
                                                         state=task_state, object_id=object_id)
        return taskcreate
    return wrap_task

def do_update_glance(context,keyed_args,state):
    try:
        image =getattr(keyed_args,'image',None)
        taskopts.TaskOpteration.do_task_save(context,glanceobject(),state=state, object_id=image.image_id,
                                         object_name=image.name)
    except exception.NotFound:
        LOG.warning(_LW("can not find the task"))

    except Exception as e:
        LOG.error(_LE("the error of create instance task is %s"), str(e))
        state = 'error'
        taskopts.TaskOpteration.do_task_save(context,glanceobject(),state=state)


def glanceupdatetask(currentstate=None,nextstate=None):
    def wrap_task(f):
        @wraps(f)
        def taskupdate(self,context,*args,**kwargs):
            state = None
            keyed_args, newcontext = utils.get_context_args(f, self, context, *args, **kwargs)
            if currentstate:
                do_update_glance(currentstate, context, keyed_args)
            try:
                return f(self, context, *args, **kwargs)
            except Exception:
                with excutils.save_and_reraise_exception():
                    state = 'failed'
                    taskopts.TaskOpteration.do_task_save(newcontext, glanceobject(),state=state)
            finally:
                if nextstate and not state:
                    do_update_glance(nextstate, newcontext, keyed_args)
        return taskupdate
    return  wrap_task