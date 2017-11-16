from __future__ import print_function
import functools
import sys
from config import cfg
import six
import oslo_task.conf
from oslo_task import setup
from oslo_task.db.sqlalchemy import migration
from oslo_task import exception
from oslo_task._i18n import _
from oslo_task import utils

args=utils.args

OSLO_CONF = oslo_task.conf.OSLO_CONF

def get_action_fn():
    fn = OSLO_CONF.category.action_fn
    fn_args = []
    for arg in OSLO_CONF.category.action_args:
        if isinstance(arg, six.binary_type):
            arg = arg.decode('utf-8')
        fn_args.append(arg)

    fn_kwargs = {}
    for k in OSLO_CONF.category.action_kwargs:
        v = getattr(OSLO_CONF.category, 'action_kwarg_' + k)
        if v is None:
            continue
        if isinstance(v, six.binary_type):
            v = v.decode('utf-8')
        fn_kwargs[k] = v

    # call the action with the remaining arguments
    # check arguments
    missing = utils.validate_args(fn, *fn_args, **fn_kwargs)
    if missing:
        # NOTE(mikal): this isn't the most helpful error message ever. It is
        # long, and tells you a lot of things you probably don't want to know
        # if you just got a single arg wrong.
        print(fn.__doc__)
        OSLO_CONF.print_help()
        raise exception.Invalid(
            _("Missing arguments: %s") % ", ".join(missing))

    return fn, fn_args, fn_kwargs


class DbCommands(object):
    """Class for managing the main database."""

    def __init__(self):
        pass

    @args('--version', metavar='<version>', help='Database version')
    @args('--local_cell', action='store_true',
          help='Only sync db in the local cell: do not attempt to fan-out'
               'to all cells')
    def sync(self, version=None, local_cell=False):
        """Sync the database up to the most recent version."""
        return migration.db_sync(version)

    def version(self):
        """Print the current database version."""
        print(migration.db_version())



CATEGORIES = {
    'db': DbCommands,
}
add_command_parsers = functools.partial(utils.add_command_parsers,
                                        categories=CATEGORIES)

category_opt = cfg.SubCommandOpt('category',
                                 title='Command categories',
                                 help='Available categories',
                                 handler=add_command_parsers)
def main():
    """Parse options and call the appropriate class/method."""
    OSLO_CONF.register_cli_opt(category_opt)
    setup.setup(sys.argv[2])
    try:
        fn, fn_args, fn_kwargs = get_action_fn()
        ret = fn(*fn_args, **fn_kwargs)
        return(ret)
    except Exception as ex:
        print(_("error: %s") % ex)
        return(1)