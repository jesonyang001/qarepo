.. _localization:
======================================
Configuring language support in Askbot
======================================

There are several things to consider when localizing askbot:

* :ref:`setting the site language <default-lang>`
* :ref:`translation and display of the urls <translate-urls>`
* :ref:`translation of the strings in the user interface <strings>`
* :ref:`enabling the multilingual setup <multilingual>`
* :ref:`configuring the language-specific text search <text-search>`

.. _default-lang:

Setting the site language
=========================

Specify the language code with the value of `LANGUAGE_CODE` parameter 
in the `settings.py` file::

    LANGUAGE_CODE='es'

.. note::
    In the :ref:`multi-lingual configuration <multilingual>`
    this language will be the default and the complete list of
    language codes and their verbose names 
    is specified with the `LANGUAGES` parameter.

.. _translate-urls:

Translation of the URLs
=======================

There are also `settings.py` options to translate the urls: 
`ASKBOT_TRANSLATE_URL` and `ALLOW_UNICODE_SLUGS`.

When the `ASKBOT_TRANSLATE_URL` is `True`, most urls will be translated, 
otherwise urls will be in English.
When the `ALLOW_UNICODE_SLUGS` is `True` the question titles and user names
will be presented as Unicode, e.g. with the Cyrillic, Chinese 
or Arabic characters, otherwise they will be transliterated into ASCII.

If you are translating URLs (in the transifex you will probably 
find them as strings containing forward slashes) - 
take the following, in order to prevent broken links:

* translation of multiple urls cannot be the same 
  (e.g. /question/ and /questions/ must have different translations)
* if the same url is present in more than one translation file
  those translation must be exactly the same

.. _strings:

Translation of strings in Askbot
================================

Translation of Askbot strings is performed at the `Transifex service <transifex>`_.
Please `register there <transifex>`_ and work on the localization that interests you. 
We periodically update the source language strings on Transifex and pull 
the translations back into the project. Thanks!

If you intend to translate urls - please :ref:`look here <translate-urls>`.

Please *do not* translate via github (if you know what it means),
as it's better to have just one source of strings.

The remaining part will will most likely interest developers, 
therefore here we tell what is specific to Askbot and
refer the developer to the documentation of tools
used in Askbot.

Firstly - Askbot uses `Jinja2 <http://jinja.pocoo.org/docs/>`_ templates,
not the Django templates and an Jinja2 adapter module for Django, called
`Coffin <https://github.com/coffin/coffin/>`_. Please look at how translation
tags are added to the templates processed by the `coffin` module.

Secondly - instead of the django `makemessages` command - use `jinja2_makemessages`.

Finally - to pull strings from the transifex use the `tx` program from 
`transifex-client pypi package <https://pypi.python.org/pypi/transifex-client>`_.
