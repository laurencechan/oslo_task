import copy
import argparse
import six
from oslo_utils import timeutils
import inspect
from nova import safe_utils

def make_uuid(context,type):
    request_id=context.request_id
    id_content = request_id.split('-')
    if type == "task":
        id_content[0]='task'
    elif type == "event":
        id_content[0]='event'
    uuid = '-'.join(id_content)
    return uuid

def reset_context_db_part(context):
    new_context=copy.deepcopy(context)
    if hasattr(new_context,'_enginefacade_context'):
        new_context._enginefacade_context=None
    else:
        setattr(new_context,'_enginefacade_context',None)
    return new_context

def set_timestamp():
    return {
        'created_at':timeutils.utcnow(),
        'updated_at':timeutils.utcnow(),
    }
def make_initial_task_values(context,object_id,object_name,task_state,task_name,istask):
    task_values={}
    task_values['uuid']=make_uuid(context,'task')
    user_ip=context.remote_address if not getattr(context,'X-Forwarded-For',None) \
                else getattr(context,'X-Forwarded-For')
    task_values['user_ip']=user_ip
    task_values['task']=task_name
    task_values['object_id']=object_id
    task_values['object_name']=object_name
    task_values['state']=task_state
    task_values['user_id']=context.user_id
    task_values['project_id']=context.project_id
    task_values['finished_at']=None
    task_values['istask']=istask
    task_values.update(set_timestamp())
    return task_values

def get_context_args(function,self,context,*args,**kwargs):
    wrapped_func = safe_utils.get_wrapped_function(function)
    keyed_args = inspect.getcallargs(wrapped_func, self, context,
                                     *args, **kwargs)
    new_context = reset_context_db_part(context)
    return keyed_args,new_context

def get_nova_req_args(function,self,req,*args,**kwargs):
    wrapped_func = safe_utils.get_wrapped_function(function)
    keyed_args = inspect.getcallargs(wrapped_func, self, req,
                                     *args, **kwargs)
    new_context = reset_context_db_part(req.environ['nova.context'])
    return keyed_args, new_context


def get_glance_req_args(function,self,req,*args,**kwargs):
    wrapped_func = safe_utils.get_wrapped_function(function)
    keyed_args = inspect.getcallargs(wrapped_func, self, req,
                                     *args, **kwargs)
    import pdb
    pdb.set_trace()
    new_context=req.context
    setattr(new_context, '_enginefacade_context', None)
    return keyed_args, new_context


def validate_args(fn, *args, **kwargs):
    """Check that the supplied args are sufficient for calling a function.

    >>> validate_args(lambda a: None)
    Traceback (most recent call last):
        ...
    MissingArgs: Missing argument(s): a
    >>> validate_args(lambda a, b, c, d: None, 0, c=1)
    Traceback (most recent call last):
        ...
    MissingArgs: Missing argument(s): b, d

    :param fn: the function to check
    :param arg: the positional arguments supplied
    :param kwargs: the keyword arguments supplied
    """
    argspec = inspect.getargspec(fn)

    num_defaults = len(argspec.defaults or [])
    required_args = argspec.args[:len(argspec.args) - num_defaults]

    if six.get_method_self(fn) is not None:
        required_args.pop(0)

    missing = [arg for arg in required_args if arg not in kwargs]
    missing = missing[len(args):]
    return missing


# Decorators for actions
def args(*args, **kwargs):
    """Decorator which adds the given args and kwargs to the args list of
    the desired func's __dict__.
    """
    def _decorator(func):
        func.__dict__.setdefault('args', []).insert(0, (args, kwargs))
        return func
    return _decorator

def methods_of(obj):
    """Get all callable methods of an object that don't start with underscore

    returns a list of tuples of the form (method_name, method)
    """
    result = []
    for i in dir(obj):
        if callable(getattr(obj, i)) and not i.startswith('_'):
            result.append((i, getattr(obj, i)))
    return result

def add_command_parsers(subparsers, categories):
    """Adds command parsers to the given subparsers.

    Adds version and bash-completion parsers.
    Adds a parser with subparsers for each category in the categories dict
    given.
    """
    parser = subparsers.add_parser('version')

    parser = subparsers.add_parser('bash-completion')
    parser.add_argument('query_category', nargs='?')

    for category in categories:
        command_object = categories[category]()

        desc = getattr(command_object, 'description', None)
        parser = subparsers.add_parser(category, description=desc)
        parser.set_defaults(command_object=command_object)

        category_subparsers = parser.add_subparsers(dest='action')

        for (action, action_fn) in methods_of(command_object):
            parser = category_subparsers.add_parser(action, description=desc)

            action_kwargs = []
            for args, kwargs in getattr(action_fn, 'args', []):
                # FIXME(markmc): hack to assume dest is the arg name without
                # the leading hyphens if no dest is supplied
                kwargs.setdefault('dest', args[0][2:])
                if kwargs['dest'].startswith('action_kwarg_'):
                    action_kwargs.append(kwargs['dest'][len('action_kwarg_'):])
                else:
                    action_kwargs.append(kwargs['dest'])
                    kwargs['dest'] = 'action_kwarg_' + kwargs['dest']

                parser.add_argument(*args, **kwargs)

            parser.set_defaults(action_fn=action_fn)
            parser.set_defaults(action_kwargs=action_kwargs)

            parser.add_argument('action_args', nargs='*',
                                help=argparse.SUPPRESS)

