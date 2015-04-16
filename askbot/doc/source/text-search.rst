.. _text-search:
======================================
Configuring full text search in Askbot
======================================

Currently there are two supported language-aware mechanisms for full text search:

* :ref:`postgresql full text search <postgresql-text-search>`
* :ref:`Solr search engine <solr-text-search>`

MySQL supports text search only for English and only for the MyISAM storage engine.
MyISAM engine lacks support of the database transactions, 
therefore it is strongly recommended to use Postgresql.

.. _postgresql-text-search:

Postgresql full text search
===========================

Postgresql supports full text search in the following languages:

Danish, Dutch, English, Finnish, French, German, Hungarian,
Italian, Japanese (requires postgresql package `textsearch_ja`), Norwegian,
Portugese, Romanian, Russian, Spanish, Swedish, Turkish.

To enable this option - just use the postgresql database and
add in the `settings.py` file
the corresponding entry in the 
`LANGUAGES setting <https://docs.djangoproject.com/en/dev/ref/settings/#languages>`_.

.. note::
    Japanese language search in Postgresql requires installation
    of a "contrib" package called `textsearch_ja`

.. _solr-text-search:

Solr full text search
=====================

Apache Solr search supports more languages and Askbot supports Solr via the
module called Haystack.

:ref:`Here <solr>` are detailed instructions on how to enable Solr on 
Ubuntu system version 12.04, which may be helpful for users of other 
distributions of Linux.

In addition to the basic set up of Solr, it will be necessary to configure
:ref:`multilingual search <solr-multilingual>` under solr.
