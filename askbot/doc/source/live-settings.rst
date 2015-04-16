.. _live-settings:
=============
Live settings
=============

Many of the configuration settings in askbot are accessible
to the site administators via link "settings" in the site header.

Any change to the "live settings" will be reflected on the site
immediately.

No-one but the site administrators can change those settings.

.. note::
    Any user can be turned into an administrator via running a command.

        python manage.py add_admin <user_id>

    At the moment this command is not available from the web-interface
    but this will be fixed in the future.

.. _live-settings-options:
Entering live settings in settings.py file
==========================================

You might want to bypass live settings and enter them directly
in the ``settings.py`` file.

Currently there are two ways to do this:

1. Simply add variable with the same name as defined in `askbot/conf` files, 
   but prefixed with `ASKBOT_` and the corresponding value.
   For example, add `ASKBOT_RSS_ENABLED = False` to disable the rss.
   In `askbot/conf` this value is defined simply as `RSS_ENABLED`.

2. Put settings into the ``LIVESETTINGS_OPTIONS`` dictionary,
   this way you can assign livesettings values to specific site by ID,
   which may or may not be useful for the multi-portal (multi-site) askbot setup.

The first method above overrides the second.

Here is a more detailed description on how to use the `LIVESETTINGS_OPTIONS` method:

Having live settings overridden from the ``settings.py`` file may
somewhat speed up your site
and
decrease a chance that the values could be accessed
by an unauthorized person.

Please see an example below::

    LIVESETTINGS_OPTIONS = {
        1: {
            'DB' : True,
            'SETTINGS': {
                'EMAIL': {
                    'REPLY_BY_EMAIL': True
                }
            }
    }

Firstly, the number "1" is site id. Most
likely the number should be the same as the value of ``SITE_ID`` setting.

The value for the site id key is a nested dictionary with two keys:
``'DB'`` (if True - then the rest of settings will be taken from the database) 
and ``'SETTINGS'`` - a dictionary with the actual settings.
In this example ``'EMAIL'`` is the settings group
and
``'REPLY_BY_EMAIL'`` is the setting name, with ``True`` being the value.

Setting group names and setting names can be looked up in files within 
``askbot/conf`` directory.
