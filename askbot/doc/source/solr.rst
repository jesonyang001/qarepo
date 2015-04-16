.. _solr:

===========================================================
Installing Apache Solr with Apache Tomcat 7 in Ubuntu 12.04
===========================================================


This document describes the process of instalation of Apache Solr search engine in Ubuntu Server  12.04
for askbot use. To follow this steps you must have already askbot installed and running.

Installation of the required packages
=====================================

Install packages `tomcat7` and `tomcat7-admin`::

    sudo apt-get install tomcat7 tomcat7-admin

Download Apache Solr from the `official site <http://lucene.apache.org/solr/downloads.html>`_::

    wget http://www.bizdirusa.com/mirrors/apache/lucene/solr/3.6.2/apache-solr-3.6.2.tgz 

Install `django-haystack` module in your Python environment::
    
    pip install django-haystack

Setting up Tomcat
=================

After installing Tomcat, add users to the Tomcat server. 
Edit `/etc/tomcat7/tomcat-users.xml` and add the following::

    <?xml version='1.0' encoding='utf-8'?>
    <tomcat-users>
      <role rolename="manager"/>
      <role rolename="admin"/>
      <role rolename="admin-gui"/>
      <role rolename="manager-gui"/>
      <user username="tomcat" password="tomcat" 
          roles="manager,admin,manager-gui,admin-gui"/>
    </tomcat-users>

Then restart the service::

    service tomcat7 restart

Now you should be able to connect to the web management interface 
via http://youripaddress:8080/manager 
and entering there user name and password.

Installing Solr under Tomcat
============================

Extract the solr tar archive from the previous download::

    tar -xzf apache-solr-3.6.2.tgz

Copy the `example/` directory from the source to `/opt/solr/`. 
Open the file `/opt/solr/example/solr/conf/solrconfig.xml` 
and Modify the dataDir parameter as:: 

    <dataDir>${solr.data.dir:/opt/solr/example/solr/data}</dataDir>

Copy the `.war` file in dist directory to `/opt/solr`::

    cp dist/apache-solr-3.6.2.war  /opt/solr

Create `solr.xml` inside of `/etc/tomcat/Catalina/localhost/` with the following contents::

    <?xml version="1.0" encoding="utf-8"?>
    <Context docBase="/opt/solr/apache-solr-3.6.2.war" debug="0" crossContext="true">
      <Environment name="solr/home" type="java.lang.String" 
         value="/opt/solr/example/solr" override="true"/>
    </Context>

Restart the tomcat server::
    
    service tomcat7 restart

Now you should be able to access the "solr" application
in the Tomcat manager at `/solr/admin`.

Configuring Askbot with Solr
============================

Open settings.py file and configure the following::

    ENABLE_HAYSTACK_SEARCH = True
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
            'URL': 'http://127.0.0.1:8080/solr'
        }
    }

After that create the solr schema and store the output to your solr instalation::

    python manage.py build_solr_schema > /opt/solr/example/solr/conf/schema.xml

Restart tomcat server::
    
    service tomcat7 restart

Build the Index for the first time::

    python manage.py rebuild_index

The output should be something like::

    All documents removed.
    Indexing 43 people.
    Indexing 101 posts.
    Indexing 101 threads.

Now all should be ready,
just restart the askbot application 
and test the search with haystack and solr.

.. _solr-multilingual:

Multilingual Setup
==================

.. note::
    This is experimental feature, currently xml generation works for: 
    English, Spanish, Chinese, Japanese, Korean and French.

Add the following to settings.py::

    HAYSTACK_ROUTERS = ['askbot.search.haystack.routers.LanguageRouter',]

Configure the HAYSTACK_CONNECTIONS settings with the following format for each language::

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
            'URL': 'http://127.0.0.1:8080/solr'
        },
        'default_<language_code>': {
            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
            'URL': 'http://127.0.0.1:8080/solr/core-<language_code>'
        },
    }

Generate xml files according to language::

    python manage.py askbot_build_solr_schema -l <language_code> > /opt/solr/example/solr/conf/schema-<language_code>.xml 

Add cores to Solr
-----------------

For each language that you want to support you will need to add a solr core like this::

    http://127.0.0.1:8080/solr/admin/cores?action=CREATE&name=core-<language_code>&instanceDir=.&config=solrconfig.xml&schema=schema-<language_code>.xml&dataDir=data

For more information on how to handle Solr cores visit the
`Solr documetation <http://wiki.apache.org/solr/CoreAdmin>`_.

Build the index according to language
-------------------------------------

For every active language rebuild the index::

    python manage.py askbot_rebuild_index -l <language_code>


Keeping the search index fresh
==============================

There are several ways to keep the index fresh in askbot with haystack.

Cronjob
-------

Create a cronjob that executes *askbot_update_index* command 
for each of the activated languages.

Real Time Signal
----------------

The *real time* signal method updates the index synchronously 
after each object it's  saved or deleted, 
to enable it add this to settings.py::

    HAYSTACK_SIGNAL_PROCESSOR = 'askbot.search.haystack.signals.AskbotRealtimeSignalProcessor'

Use of synchronous index updates may slow down your site
which may not be acceptable for the high traffic sites.

Updating the Index asyncronously with Celery
--------------------------------------------

The *asynchronous signal* method updates the index by adding delayed job to the queue
after each object is saved or deleted. 

To make this work, 
`django-celery <http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html>`_
must be installed, enabled and configured and the Haystack signal processor configured
in the `settings.py` file::

    HAYSTACK_SIGNAL_PROCESSOR = 'askbot.search.haystack.signals.AskbotCelerySignalProcessor'
    #modify CELERY_ALWAYS_EAGER to:
    CELERY_ALWAYS_EAGER = False
