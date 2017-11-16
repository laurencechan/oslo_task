#coding=utf-8
from functools import wraps
from oslo_utils import excutils
from oslo_log import log as logging
from oslo_task._i18n import _LE,_LW
from oslo_task import utils
from nova.compute import vm_states
from oslo_task import exception
from oslo_task.tasks import opts as taskopts
from oslo_task.tasks import novatask
LOG = logging.getLogger(__name__)

FLAVOR_TASK=['创建虚机配置','删除虚机配置','移除租户使用权','增加租户使用权']
KEYPAIR_TASK=['创建密钥对','导入密钥对','删除密钥对']
SIMPLE_TASK=FLAVOR_TASK+KEYPAIR_TASK

novaobject=novatask.NovaTask
#nova decorator
def novataskcreate(task_name,IsTask=False):
    def _create_decorator(func):
        @wraps(func)
        def _decorator(self,req,*args,**kwargs):
            name=None
            task_state='start'
            keyed_args,new_context=utils.get_nova_req_args(func,self,req,*args,**kwargs)
            object_id = keyed_args.get('id',None)
            body=keyed_args.get('body',None)
            if  body:
                if body.has_key('server'):
                    if body['server']['min_count']>1:
                       name="批量创建虚拟机"
                elif body.has_key('reboot'):
                    name="软重启" if body['reboot']['type'].upper()=='SOFT' else "硬重启"
                elif body.has_key('keypair'):
                    name="导入密钥对" if 'public_key' in body['keypair'] else "创建密钥对"
            try:
                name = task_name if not name else name
                taskopts.TaskOpteration.do_task_create(new_context,novaobject(),object_id, task_state,name,None,IsTask)
            except exception.CreateFailed:
                LOG.error(_LE("create a task failed"))
            except Exception as e:
                LOG.error(_LE("It's a unknown error in create task,error is %s"), str(e))
                task_state = 'error'
                taskopts.TaskOpteration.do_task_save(new_context,novaobject(),state=task_state, object_id=object_id)
            try:
                return func(self,req,*args,**kwargs)
            except Exception:
                with excutils.save_and_reraise_exception():
                    task_state = 'failed'
                    taskopts.TaskOpteration.do_task_save(new_context,novaobject(),state=task_state,object_id=object_id)
            finally:
                if name in SIMPLE_TASK and task_state not in ['failed','error']:
                    state = 'success'
                    taskopts.TaskOpteration.do_task_save(new_context,novaobject(),state=state)
        return _decorator
    return _create_decorator

def _populate_task(context,task_state,instance):
    if task_state not in['failed','error'] and instance.task_state is None:
        task_state='success'
    taskopts.TaskOpteration.do_task_save(context, novaobject(),state=task_state, object_id=instance.uuid,
                      object_name=instance.display_name)

def _do_update_task(keyed_args,context,state):
    try:
        if keyed_args.has_key('instance'):
            if not state :
                state='start'
            instance = keyed_args['instance']
            _populate_task(context, state, instance)
        else:
            taskopts.TaskOpteration.do_task_save(context,novaobject(),state=state)
    except Exception as e:
        LOG.error(_LE("It's a error happening in create task,error is %s"), str(e))
        state = 'error'
        taskopts.TaskOpteration.do_task_save(context,novaobject(),state=state)

def novatasksave(task_state=None):
    def _update_wraps(f):
        @wraps(f)
        def taskwraps(self,context,*args,**kwargs):
            state=task_state
            keyed_args, newcontext = utils.get_context_args(f, self, context, *args, **kwargs)
            try:
                return f(self,context,*args,**kwargs)
            except Exception:
                with excutils.save_and_reraise_exception():
                    state = 'failed'
            finally:
                _do_update_task(keyed_args, newcontext, state)
        return taskwraps
    return _update_wraps


def _do_update_task_state(state,context,keyed_args):
    task_id = utils.make_uuid(context, 'task')
    instances = keyed_args['instances'] if keyed_args.has_key('instances') else [keyed_args['instance']]
    try:
        obj_task = taskopts.TaskOpteration.get_by_task_id(context,novaobject,task_id)
        if obj_task.task == "批量创建虚拟机":
            pass
        else:
            if instances[0].vm_state == vm_states.ERROR:
                state = 'failed'
            taskopts.TaskOpteration.do_task_save(context, novaobject(),state=state, object_id=instances[0].uuid,
                          object_name=instances[0].display_name)
    except exception.NotFound:
        LOG.warning(_LW("can not find the task"))
    except Exception as e:
        LOG.error(_LE("the error of create instance task is %s"), str(e))
        state = 'error'
        taskopts.TaskOpteration.do_task_save(context, novaobject(),state=state)

def updatetask(current_state=None,next_state=None):
    def vmcreate(f):
        @wraps(f)
        def task_create(self,context,*args,**kwargs):
            state=None
            keyed_args, newcontext = utils.get_context_args(f, self, context, *args, **kwargs)
            if current_state:
                _do_update_task_state(current_state,context,keyed_args)
            try:
                return f(self,context,*args,**kwargs)
            except Exception:
                with excutils.save_and_reraise_exception():
                    state = 'failed'
                    taskopts.TaskOpteration.do_task_save(newcontext,novaobject(),state=state)
            finally:
                 if next_state and not state :
                     _do_update_task_state(next_state, newcontext, keyed_args)
        return task_create
    return vmcreate




