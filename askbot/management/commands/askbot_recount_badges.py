"""Recounts user's badges"""
from askbot import const
from askbot.models import User
from askbot.utils.console import ProgressBar
from django.core.management.base import NoArgsCommand
from django.db import transaction

class Command(NoArgsCommand):

    @transaction.commit_manually
    def handle_noargs(self, *args, **kwargs):
        users = User.objects.all()
        count = users.count()
        msg = 'Counting user badges'
        for user in ProgressBar(users.iterator(), count, msg):
            user.recount_badges()
            transaction.commit()
