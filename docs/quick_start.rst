Quick Start Guide
=================


Download Muss forum Project
---------------------------

First, you need to download Muss from GitHub.

You can visit the repository webpage in |muss_github| and download it as a zip file.


.. |muss_github| raw:: html

    <a href="https://github.com/mapeveri/muss" target="_blank">Github</a>

You can also do the same using your terminal with::

    $ git clone git@github.com:mapeveri/muss.git


**Important**

Make sure you have a |redis_installer_link|

.. |redis_installer_link| raw:: html

    <a href="https://redis.io/topics/quickstart" target="_blank">redis installer.</a>


Install the requirements
------------------------

Next, located in the root directory project, install the packages dependencies inside your virtual environment::

    $ pip install -r requirements.txt


Go to the folder /conf/ and rename file settings_local.py.txt to settings_local.py and .env.example to .env. Then configure thats variables.
These variables are to configure the database and secret key of Django.

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

Copy this value and paste it instead of **your_secret_django_key** value to the file conf/.env.
With this previous step will be include your new **Django SECRET_KEY** inside your project

Migrating and create super user
-------------------------------

We sync the changes to the database::

    $ python manage.py migrate
    $ python manage.py createsuperuser


Setup the admin
~~~~~~~~~~~~~~~

Execute::

    $ python manage.py config_admin



Internationalization and Localization
-------------------------------------


Settings
~~~~~~~~

The default language for this Project is **English**, and the internationalization is used to translate the text to
Spanish and Italian languages.

If you want to change the translation language, you just need to modify the **LANGUAGE_CODE** variable in the file *conf/settings.py*.

Set variable GOOGLE_MAPS_API_KEY with API_KEY value of `Google maps`_.

.. _Google maps: https://developers.google.com/maps/faq?hl=es-419#new-key


Translation
~~~~~~~~~~~

Go to the terminal, inside the muss folder and create the files to translate with::

    $ python manage.py compilemessages


Admin
~~~~~

In django admin go to application site and edit record with the full url of the site (Example: http://www.myforum.com).

Configuration forum
~~~~~~~~~~~~~~~~~~~

For custom forum go to application **Configuration**. In the application you can change design, upload logo and favicon, etc.


Frontend
~~~~~~~~

Now, Go to the folder */static/muss* and execute::

    $ npm install
    $ bower install


Continue to the :doc:`dev`!
