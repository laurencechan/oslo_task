#coding=utf-8
from oslo_task._i18n import _
#object对象需要对应的组件注册版本类装饰器装饰
#NOTE:novaregister = base.NovaObjectRegistry.register
#远程调用的装饰器，在nova中是隐式调用rpc函数发送到conductor
#remotable=base.remotable
#remotable_classmethod = base.remotable_classmethod
class TaskBase(object):

    def save(self, context):
        """Save the changed fields back to the store.

        This is optional for subclasses, but is presented here in the base
        class for consistency among those that do.
        """
        raise NotImplementedError(_('Cannot save anything in the base class'))

    def add(self, context):
        """Save the changed fields back to the store.

        This is optional for subclasses, but is presented here in the base
        class for consistency among those that do.
        """
        raise NotImplementedError(_('Cannot save anything in the base class'))



