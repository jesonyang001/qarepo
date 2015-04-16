from django.core.management.base import NoArgsCommand
from django.core.cache import cache

class Command(NoArgsCommand):
    def handle_noargs(self, *args, **kwargs):
        cache.clear()
