"""
Options for multilingual models
"""
from django.db.models.fields import FieldDoesNotExist
from django.db.models.options import Options


class MultilingualOptions(Options):
    """
    These options are mainly used for creation of SQL commands.
    Do not mess it up unless you make sure that this will work correctly for database.
    """
    def __init__(self, meta, app_label=None):
        self.translation_model = None
        super(MultilingualOptions, self).__init__(meta, app_label)

    def get_virtual_field(self, name):
        """
        Returns the requested virtual field by name. Raises FieldDoesNotExist on error.
        """
        for field in self.virtual_fields:
            if field.name == name:
                return field
        raise FieldDoesNotExist('%s has no virtual field named %r' % (self.object_name, name))
