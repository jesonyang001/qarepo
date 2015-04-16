from django.core.management.base import NoArgsCommand
from django.template.loader import get_template
from django.utils.translation import ugettext as _
from askbot.conf import settings as askbot_settings
from askbot import const
from askbot import mail
from askbot.mail.messages import ModerationQueueNotification
from askbot.models import Activity
from askbot.models import User

def get_moderators():
    return User.objects.filter(status__in=('d', 'm'))

def get_last_mod_alert_activity():
    atype = const.TYPE_ACTIVITY_MODERATION_ALERT_SENT
    acts = Activity.objects.filter(activity_type=atype).order_by('-id')
    count = len(acts)
    if count == 0:
        return None
    last_act = acts[0]

    if count > 1:
        #get last moderation activity and delete all others
        acts = acts.exclude(id=last_act.id)
        acts.delete()

    return last_act


def get_last_notified_user():
    last_act = get_last_mod_alert_activity()
    if last_act:
        return last_act.content_object
    return None


def select_moderators_to_notify(candidates, num_needed):
    candidates_count = candidates.count()

    #special case - if we need to notify the same number of
    #moderators that are available, then we don't rotate them
    #and notify all, b/c otherwise we would stop notifications
    #because there are not enough moderators
    if candidates_count <= num_needed:
        return list(candidates)

    last_notified = get_last_notified_user()
    if last_notified is None:
        return candidates[:num_needed]

    mods = list(candidates.filter(id__gt=last_notified.id))
    num_mods = len(mods)
    if num_mods >= num_needed:
        return mods[:num_needed]
    else:
        #wrap around the end to the beginning
        num_missing = num_needed - num_mods
        more_mods = get_moderators().order_by('id')
        more_mods = more_mods[:num_missing]
        mods.extend(list(more_mods))
        return mods


def select_last_moderator(mods):
    return max(mods, key=lambda item: item.id)


def remember_last_moderator(user):
    act = get_last_mod_alert_activity()
    if act:
        act.content_object = user
        act.save()
    else:
        act = Activity(
            user=user,
            content_object=user,
            activity_type=const.TYPE_ACTIVITY_MODERATION_ALERT_SENT
        )
        act.save()


class Command(NoArgsCommand):
    def handle_noargs(self, *args, **kwargs):
        #get size of moderation queue
        queue = Activity.objects.filter(activity_type__in=const.MODERATED_ACTIVITY_TYPES)
        if queue.count() == 0:
            return

        #get moderators
        mods = get_moderators().order_by('id')
        if mods.count() == 0:
            return

        mods = select_moderators_to_notify(mods, 3)

        if len(mods) == 0:
            return

        for mod in mods:
            email = ModerationQueueNotification({'user': mod})
            email.send([mod,])

        last_mod = select_last_moderator(mods)
        remember_last_moderator(last_mod)
