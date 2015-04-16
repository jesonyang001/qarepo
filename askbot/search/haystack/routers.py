from haystack.routers import BaseRouter
from haystack.constants import DEFAULT_ALIAS

from .utils import alias_from_language, get_language


class LanguageRouter(BaseRouter):

    def for_read(self, **hints):
        from django.conf import settings

        if getattr(settings, 'ASKBOT_MULTILINGUAL'):
            language = get_language()
            return alias_from_language(language)
        else:
            return DEFAULT_ALIAS

    def for_write(self, **hints):
        from django.conf import settings

        if getattr(settings, 'ASKBOT_MULTILINGUAL'):
            language = get_language()
            return alias_from_language(language)
        else:
            return DEFAULT_ALIAS
