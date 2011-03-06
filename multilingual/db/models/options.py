from django.db.models.loading import app_cache_ready
from django.db.models.options import Options


class MultilingualOptions(Options):
    def __init__(self, meta, app_label=None):
        self.translation_model = None
        super(MultilingualOptions, self).__init__(meta, app_label)
