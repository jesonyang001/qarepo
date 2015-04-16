from django.core.management.base import NoArgsCommand
from django.db.models import Q
from django.template.loader import get_template
from askbot import models
from askbot import const
from askbot.conf import settings as askbot_settings
from django.utils.translation import ungettext
from askbot.mail.messages import UnansweredQuestionsReminder
from askbot.utils.classes import ReminderSchedule
from askbot.models.question import Thread
from askbot.utils.html import site_url
from django.template import Context

DEBUG_THIS_COMMAND = False

class Command(NoArgsCommand):
    """management command that sends reminders
    about unanswered questions to all users
    """
    def handle_noargs(self, **options):
        if askbot_settings.ENABLE_EMAIL_ALERTS == False:
            return
        if askbot_settings.ENABLE_UNANSWERED_REMINDERS == False:
            return
        #get questions without answers, excluding closed and deleted
        #order it by descending added_at date
        schedule = ReminderSchedule(
            askbot_settings.DAYS_BEFORE_SENDING_UNANSWERED_REMINDER,
            askbot_settings.UNANSWERED_REMINDER_FREQUENCY,
            max_reminders = askbot_settings.MAX_UNANSWERED_REMINDERS
        )

        questions = models.Post.objects.get_questions()

        #we don't report closed, deleted or moderation queue questions
        exclude_filter = Q(thread__closed=True) | Q(deleted=True)
        if askbot_settings.CONTENT_MODERATION_MODE == 'premoderation':
            exclude_filter |= Q(approved=False)
        questions = questions.exclude(exclude_filter)

        #select questions within the range of the reminder schedule
        questions = questions.added_between(
                        start=schedule.start_cutoff_date,
                        end=schedule.end_cutoff_date
                    )

        #take only questions with zero answers
        questions = questions.filter(thread__answer_count=0)

        if questions.count() == 0:
            #nothing to do
            return

        questions = questions.order_by('-added_at')

        if askbot_settings.UNANSWERED_REMINDER_RECIPIENTS == 'admins':
            recipient_statuses = ('d', 'm')
        else:
            recipient_statuses = ('a', 'w', 'd', 'm')

        #for all users, excluding blocked
        #for each user, select a tag filtered subset
        #format the email reminder and send it
        for user in models.User.objects.filter(status__in=recipient_statuses):
            user_questions = questions.exclude(author=user)
            user_questions = user.get_tag_filtered_questions(user_questions)

            if askbot_settings.GROUPS_ENABLED:
                user_groups = user.get_groups()
                user_questions = user_questions.filter(groups__in = user_groups)

            final_question_list = user_questions.get_questions_needing_reminder(
                user = user,
                activity_type = const.TYPE_ACTIVITY_UNANSWERED_REMINDER_SENT,
                recurrence_delay = schedule.recurrence_delay
            )

            question_count = len(final_question_list)
            if question_count == 0:
                continue

            email = UnansweredQuestionsReminder({
                'recipient_user': user,
                'questions': final_question_list
            })

            if DEBUG_THIS_COMMAND:
                print "User: %s<br>\nSubject:%s<br>\nText: %s<br>\n" % \
                    (user.email, email.render_subject(), email.render_body())
            else:
                email.send([user.email,])
