Quick Start Guide
=================


Download Muss forum Project
----------------------------------------------

First, you need to download Muss from GitHub.

You can visit the repository webpage in `muss github`_ and dowload it as a zip file.

.. _muss github: https://github.com/mapeveri/muss

You can also do the same using your terminal with::

    $ git clone git@github.com:mapeveri/muss.git


Install the requirements
------------------------

Next, located in the root directory project, install the packages dependencies inside your virtual environment::

    $ pip install -r requirements.txt


Go to the conf/ folder and rename **settings_local.py.txt** file  to **settings_local.py** file.

Secret Django Key
-----------------

Muss has the SECRET_KEY environment variable hidden.
You can the generate the SECRET_KEY and export environment variable of this way:


Generating the SECRET_KEY
~~~~~~~~~~~~~~~~~~~~~~~~~

Locate in the root directory and type::

    $ python script/django-secret-keygen.py

This will generate the characters combination value to **SECRET_KEY**


Defining the SECRET_KEY environment variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Copy this value and paste it instead of **your_secret_django_key** value::

    $ export SECRET_KEY="your_secret_django_key"

With this previous step will be include your new **Django SECRET_KEY** inside your project

Migrating and create super user
-------------------------------

We sync the changes to the database::

    $ python manage.py migrate
    $ python manage.py createsuperuser

