#coding=utf-8
from oslo_task.db.sqlalchemy import api as sqlalchemy_api
import oslo_task.conf
from oslo_db import options as oslo_db_options

OSLO_CONF=oslo_task.conf.OSLO_CONF
def make_file_args(config_file):
    new_config_arg='--config-file='+config_file
    return (new_config_arg,)

def setup(default_config_files):
    oslo_db_options.set_defaults(OSLO_CONF)
    #default_config_files = (default_config_files,)#因为default_config_files解析是默认列表或者元组
    OSLO_CONF(args=make_file_args(default_config_files))
    sqlalchemy_api.configure(OSLO_CONF)
