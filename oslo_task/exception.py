import six
from oslo_task._i18n import _

_FATAL_EXCEPTION_FORMAT_ERRORS = False

class OsloTaskException(Exception):
    """
    Base oslo_task Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.
    """
    message = _("An unknown exception occurred")

    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = self.message
        try:
            if kwargs:
                message = message % kwargs
        except Exception:
            if _FATAL_EXCEPTION_FORMAT_ERRORS:
                raise
            else:
                # at least get the core message out if something happened
                pass
        self.msg = message
        super(OsloTaskException, self).__init__(message)

    def __unicode__(self):
        # NOTE(flwang): By default, self.msg is an instance of Message, which
        # can't be converted by str(). Based on the definition of
        # __unicode__, it should return unicode always.
        return six.text_type(self.msg)

class CreateFailed(OsloTaskException):
    message = _("An object create failed :%s")

class NotFound(OsloTaskException):
    message = _("An object with the specified identifier was not found.")

class UpdateFailed(OsloTaskException):
    message = _("An object update failed :%s")