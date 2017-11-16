# Copyright 2015 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from oslo_config import cfg

placement_db_group = cfg.OptGroup('database',
                                  title='task API database options',
                                  help="""
The *Placement API Database* is a separate database which is used for the new
placement-api service. In Ocata release (14.0.0) this database is optional: if
connection option is not set, api database will be used instead.  However, this
is not recommended, as it implies a potentially lengthy data migration in the
future. Operators are advised to use a separate database for Placement API from
the start.
""")

placement_db_opts = [
    cfg.StrOpt('connection',
               default=None,
               help='',
               secret=True),
    cfg.BoolOpt('sqlite_synchronous',
                default=True,
                help=''),
    cfg.StrOpt('slave_connection',
               secret=True,
               help=''),
    cfg.StrOpt('mysql_sql_mode',
               default='TRADITIONAL',
               help=''),
    cfg.IntOpt('idle_timeout',
               default=3600,
               help=''),
    cfg.IntOpt('max_pool_size',
               help=''),
    cfg.IntOpt('max_retries',
               default=10,
               help=''),
    cfg.IntOpt('retry_interval',
               default=10,
               help=''),
    cfg.IntOpt('max_overflow',
               help=''),
    cfg.IntOpt('connection_debug',
               default=0,
               help=''),
    cfg.BoolOpt('connection_trace',
                default=False,
                help=''),
    cfg.IntOpt('pool_timeout',
               help=''),
]


def register_opts(conf):
    pass
    #conf.register_opts(placement_db_opts, group=placement_db_group)



