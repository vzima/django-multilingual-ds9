"""
Options for multilingual models
"""
from django.db.models.options import Options


class MultilingualOptions(Options):
    """
    These options are mainly used for creation of SQL commands.
    Do not mess it up unless you make sure that this will work correctly for database.
    """
    def __init__(self, meta, app_label=None):
        self.translation_model = None
        super(MultilingualOptions, self).__init__(meta, app_label)
