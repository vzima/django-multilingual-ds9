from multilingual.languages import get_active, FALLBACK_FIELD_SUFFIX


def log_missing_translation(parent, translation_name):
    #print "TRANSLATION DOES NOT EXIST", type(parent), parent.pk, translation_name
    pass
    # TODO: use django log if available
    #from  django.utils.log import debug
    #debug('some message')


class TranslationProxyField(object):
    """
    Provides an access to translated fields
    Based on GenericForeignKey field
    """
    def __init__(self, field_name, language_code=None, fallback=False):
        self._field_name = field_name
        self._language_code = language_code
        self._fallback = fallback
        names = [field_name]
        if language_code is not None:
            names.append(language_code.replace('-', '_'))
        if fallback:
            names.append(FALLBACK_FIELD_SUFFIX)
        self.name = '_'.join(names)

    def contribute_to_class(self, cls, name):
        if self.name != name:
            raise ValueError('Field proxy %s is added to class under bad attribute name.' % self)
        self.model = cls
        self.cache_attr = "_%s_cache" % name
        cls._meta.add_virtual_field(self)

        #===============================================================================================================
        # # For some reason I don't totally understand, using weakrefs here doesn't work.
        # signals.pre_init.connect(self.instance_pre_init, sender=cls, weak=False)
        #===============================================================================================================

        # Connect myself as the descriptor for this field
        setattr(cls, name, self)

    # This might be used to create multilingual model instance with translations in __init__ args
    # Example: SomeMultilingualModel(trans_field_en='some', trans_field_cs='neco')
    #===================================================================================================================
    # def instance_pre_init(self, signal, sender, args, kwargs, **_kwargs):
    #    """
    #    Handles initializing an object with the generic FK instaed of
    #    content-type/object-id fields.
    #    """
    #    if self.name in kwargs:
    #        value = kwargs.pop(self.name)
    #        kwargs[self.ct_field] = self.get_content_type(obj=value)
    #        kwargs[self.fk_field] = value._get_pk_val()
    #===================================================================================================================

    @property
    def language_code(self):
        """
        If _language_code is None we are the _current field, so we use the
        currently used language for lookups.
        """
        if self._language_code is not None:
            return self._language_code
        return get_active()

    @property
    def fallback(self):
        return self._fallback

    def __get__(self, instance, instance_type=None):
        """
        Returns field translation or None
        """
        if instance is None:
            return self

        try:
            return getattr(
                instance._get_translation(self.language_code, fallback=self.fallback),
                self._field_name
            )
        except instance._meta.translation_model.DoesNotExist:
            log_missing_translation(instance, self.name)
            return None

    def __set__(self, instance, value):
        """
        Sets field translation
        """
        if instance is None:
            raise AttributeError(u"%s must be accessed via instance" % self.name)

        translation = instance._get_translation(
            self.language_code,
            can_create=True
        )
        setattr(translation, self._field_name, value)
