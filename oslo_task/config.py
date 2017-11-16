from oslo_config import cfg
oslo_task_group = cfg.OptGroup('oslo_task',
                                  title='task API database options',
                                  help="""
The *Placement API Database* is a separate database which is used for the new
placement-api service. In Ocata release (14.0.0) this database is optional: if
connection option is not set, api database will be used instead.  However, this
is not recommended, as it implies a potentially lengthy data migration in the
future. Operators are advised to use a separate database for Placement API from
the start.
""")
opts=[cfg.StrOpt('config_file',
               default='/etc/oslo_task.conf',
               help=''),
      ]

def register_opts(conf):
    conf.register_opts(opts, group=oslo_task_group)
