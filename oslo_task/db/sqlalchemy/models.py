# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
SQLAlchemy models for task data
author:xieweijie
time:2017-10-26
"""
from oslo_db.sqlalchemy import models
from sqlalchemy import (Column, Integer, String, ForeignKey, Index,
                        UniqueConstraint, BigInteger)
from sqlalchemy import Float, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm


_COMMON_TABLE_ARGS = {'mysql_charset': "utf8", 'mysql_engine': "InnoDB"}

Base = declarative_base()

class TaskBase(models.TimestampMixin,
               models.ModelBase):
    metadata = None

    def __copy__(self):
        session = orm.Session()

        copy = session.merge(self, load=False)
        session.expunge(copy)
        return copy

class Task(Base,TaskBase):
    ''' save the task result '''
    __tablename__='tasks'
    __table_args__ =(
        Index('uuid', 'uuid', unique=True),
        Index('task_object_idx','object_id'),
        Index('task_state_idx','state'),
        Index('task_user_ip_idx','user_ip'),
        Index('task_user_idx', 'user_id'),
        Index('task_start_at_finish_at_idx', 'created_at','finished_at'),
        Index('task_project_id_idx','project_id')
    )
    id =Column(Integer, primary_key=True,nullable=False)
    uuid=Column(String(length=255),nullable=False)
    user_ip=Column(String(length=36))
    task = Column(String(length=255),nullable=False)
    object_id = Column(String(length=255))
    object_name = Column(String(length=127))
    state = Column(String(length=36))
    user_id = Column(String(length=36))
    istask = Column(Boolean,default=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    finished_at = Column(DateTime)
    project_id=Column(String(length=255))

class Event(Base,TaskBase):
    __tablename__='events'
    __table_args__ = (
        Index('uuid', 'uuid', unique=True),
        Index('event_object_id_idx','object_id'),
        Index('event_project_id_idx','project_id'),
        Index('event_user_id_idx','user_id')
    )
    id = Column(Integer, primary_key=True,nullable=False)
    uuid = Column(String(length=255),nullable=False)
    event = Column(String(length=255),nullable=False)
    object_id=Column(String(length=255))
    object_name = Column(String(length=127))
    user_id = Column(String(length=255))
    created_at = Column(DateTime)
    project_id = Column(String(length=255))