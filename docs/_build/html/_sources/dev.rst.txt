Running Muss
===============

Initially, is necessary execute the Django backend::

    $ python manage.py runserver


Next, in other console tab instance execute the frontend::

    $ npm install -g ember-cli
    $ ember s


Translate
------------------------

Located in the root directory project execute::

    $ python manage.py makemessages --ignore=static
    $ python manage.py compilemessages



