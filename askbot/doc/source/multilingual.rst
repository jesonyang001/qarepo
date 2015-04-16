.. _multilingual:
====================================
Setting up multilingual Askbot sites
====================================

Askbot can support multiple languages on a single site, in which case
urls are modified by a prefix made of a language code, e.g. 
base url /questions/ becomes /de/questions/ for the German localization.

.. note::
    If you want to learn about configuration of individual languages
    please look :ref:`here <localization>`

In order to enable the multilingual setup add the following to the 
`settings.py` file::

    ASKBOT_MULTILINGUAL=True

Also, activate the django's locale middleware by adding to the 
`MIDDLEWARE_CLASSES` the following entry::

    'django.middleware.locale.LocaleMiddleware',

There is a standard Django setting `LANGUAGES`, which enables specific languages.
By default this setting contains very many languages. 
You will likely want to narrow in the `settings.py` file 
the choice of the available languages::

    #it's important to use ugettext_lazy or ugettext_noop
    #in the settings.py file
    from django.utils.translation import ugettext_lazy as _
    LANGUAGES = (
        ('de', _('German')),
        ('en', _('English'))
    )

More on the usage of this setting can be read in the
`Django documentation <https://docs.djangoproject.com/en/dev/ref/settings/#languages>`_.

The default language should be specified with the setting `LANGUAGE_CODE`.
Users will be automatically redirected to the corresponding default language
page from the non-prefixed urls.

There are a number of `settings.py` options that control the various 
aspects of the site localization - the behaviour of the software depending on the
currently active language.. Please read more about the :ref:`Localization of Askbot <localization>`.
