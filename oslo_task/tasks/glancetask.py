from oslo_task import base
from oslo_task.db.sqlalchemy import api as db_api
#glance object
class GlanceTask(base.TaskBase):
    def __init__(self):
        self._context=None
        super(GlanceTask,self).__init__()

    def add(self,values):
        context = self._context
        db_api.task_add(context, values)

    def save(self,task_id,values):
        context = self._context
        db_api.task_update(context, task_id, values)