from oslo_task import base
from nova.objects import base as novabase
from oslo_task.db.sqlalchemy import api as db_api
from nova.objects import fields


@novabase.NovaObjectRegistry.register
class NovaTask(novabase.NovaObject,base.TaskBase):
    VERSION = '1.0'

    fields = {
        'id': fields.IntegerField(),

        'user_id': fields.StringField(nullable=True),
        'project_id': fields.StringField(nullable=True),
        'task':fields.StringField(nullable=False),
        'uuid': fields.UUIDField(nullable=False),

        'object_id': fields.StringField(nullable=True),
        'object_name': fields.StringField(nullable=True),

        'state': fields.StringField(nullable=True),

        'user_ip': fields.StringField(nullable=True),

        'created_at': fields.DateTimeField(nullable=True),
        'updated_at': fields.DateTimeField(nullable=True),
        'finished_at': fields.DateTimeField(nullable=True),
    }
    def obj_clone(self):
        """Create a copy of this instance object."""
        nobj = super(NovaTask, self).obj_clone()
        return nobj

    def obj_reset_changes(self, fields=None, recursive=False):
        super(NovaTask, self).obj_reset_changes(fields,recursive=recursive)

    def obj_what_changed(self):
        changes = super(NovaTask, self).obj_what_changed()
        return changes

    @classmethod
    def _obj_from_primitive(cls, context, objver, primitive):
        self = super(NovaTask, cls)._obj_from_primitive(context, objver,
                                                        primitive)
        return self

    @staticmethod
    def _from_db_object(context,task, db_task):
        task._context=context
        for field in task.fields:
            setattr(task, field, db_task[field])
        task.obj_reset_changes()
        return task

    def add(self,values):
        context = self._context
        db_api.task_add(context,values)

    @novabase.remotable
    def save(self,task_id,values):
        context = self._context
        db_api.task_update(context,task_id,values)

    @novabase.remotable_classmethod
    def get_by_task_id(cls,context,task_id):
        db_task=db_api.task_get_by_id(context,task_id)
        task = cls._from_db_object(context,cls(),db_task)
        return task

