Muss
====

.. image:: https://coveralls.io/repos/github/mapeveri/muss/badge.svg?branch=master
    :target: https://coveralls.io/github/mapeveri/muss?branch=master

.. image:: https://travis-ci.org/mapeveri/muss.svg?branch=master
    :target: https://travis-ci.org/mapeveri/muss

Muss is a 100% open source forum developed with Django and Ember.js.


Features
--------

1. Multiple forums and ordered by for category.
2. Support to sub-forums.
3. Count views for topics.
4. Support to topics main in top in forum.
5. Support to rss to forums.
6. Search topics in the all forums.
7. Pre-moderation of topics with multiple moderators.
8. Support of media files for topics.
9. Infinite scroll for topics and comments.
10. Notifications and email notifications.
11. Notifications and comments in real time.
12. Django-admin for moderation
13. Support check user online.
14. Support to English, Italian and Spanish languages.
15. API REST with django-rest-framework.
16. Custom configuration css.
17. Editor Markdown.
18. Message for forums.
19. Suggested Topics in topic.
20. Open and Close topic.
21. Support to likes in topics and comments.
22. Check if a user is a troll.
23. Support Open Graph.


Built With
----------

1. Python/Django
2. Ember.js
3. Semantic UI
4. PostgreSQL or MySQL (Preferably PostgreSQL)
5. Redis


Configuration and installation
------------------------------

1. Clone this repository and execute:

    pip install -r requirements.txt

2. Go to the folder /conf/ and rename file settings_local.py.txt to settings_local.py. Then configure thats variables.

3. In main folder execute:

    python manage.py migrate admin_interface

    python manage.py migrate muss

    python manage.py createsuperuser

3. Execute:

    python manage.py loaddata conf/theme.json

4. Go to the folder /static/muss and execute:

    npm install
    bower install


Development
-----------

Execute Backend:

    python manage.py runserver

Execute Fronted:

    ember s

Translates:

    python manage.py makemessages  --ignore=static

    python manage.py compilemessages


Contribute
----------

1. Fork this repo and install it
2. Follow PEP8, Style Guide for Python Code
3. Write code
4. Write unit test
5. Send pull request


Status
------

In Alpha.
