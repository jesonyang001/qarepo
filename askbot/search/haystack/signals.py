from django.db.models import signals as django_signals

from haystack.signals import RealtimeSignalProcessor

from askbot import signals as askbot_signals


class AskbotRealtimeSignalProcessor(RealtimeSignalProcessor):
    '''
    Based on haystack RealTimeSignalProcessor with some
    modifications to work with askbot soft-delete models
    '''

    def setup(self):
        super(AskbotRealtimeSignalProcessor, self).setup()

        try:
            askbot_signals.delete_question_or_answer.connect(self.handle_delete)
        except ImportError:
            pass

    def teardown(self):
        super(AskbotRealtimeSignalProcessor, self).setup()
        #askbot signals
        try:
            askbot_signals.delete_question_or_answer.disconnect(self.handle_delete)
        except ImportError:
            pass

try:
    from haystack.exceptions import NotHandled
    from celery_haystack.signals import CelerySignalProcessor
    from celery_haystack.utils import enqueue_task

    class AskbotCelerySignalProcessor(CelerySignalProcessor):

        def setup(self):
            django_signals.post_save.connect(self.enqueue_save)
            django_signals.post_delete.connect(self.enqueue_delete)
            try:
                askbot_signals.delete_question_or_answer.connect(self.enqueue_delete)
            except ImportError:
                pass


        def teardown(self):
            django_signals.post_save.disconnect(self.enqueue_save)
            django_signals.post_delete.disconnect(self.enqueue_delete)

            try:
                askbot_signals.delete_question_or_answer.disconnect(self.enqueue_delete)
            except ImportError:
                pass

        def enqueue(self, action, instance, sender, **kwargs):
            using_backends = self.connection_router.for_write(instance=instance)

            for using in using_backends:
                try:
                    connection = self.connections[using]
                    index = connection.get_unified_index().get_index(sender)
                except NotHandled:
                    continue  # Check next backend

                if action == 'update' and not index.should_update(instance):
                    continue
                enqueue_task(action, instance)
                return  # Only enqueue instance once

except ImportError:
    pass
