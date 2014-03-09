TinyBlog
========

A tiny flask blog with mongodb database!!!

This project was created to create a very clean and functional blog with Flask
and MongoDB.

The code was created based in this: https://github.com/rozza/flask-tumblelog

The main libraries used here are:
---------------------------------

- Flask
- Mongoengine (flask-mongoengine)
- WTForms (flask-wtforms)
- flask-script
- flask-admin
- flask-login
- flask-paginate
- Pillow

Features
--------

- Text, Image, Video and Quote Post
- Pages
- Administration area with login

Instalation
-----------

Create your virtualenv, and install the libs:

	$ mkvirtuelenv tinyblog
    $ pip install -r requirements.txt

Create the first user:

	$ python manage.py shell
	>>> from blog import User, ROLE_ADMIN
	>>> u = User(login="admin",email="admin@yourdomain.com",role=ROLE_ADMIN,password="<thepassword>")
	>>> u.save()

Then, run the blog:

    $ python manage.py runserver

LICENCE
-------

The code is under the latest LGPL license.
http://www.gnu.org/copyleft/lesser.html

You want to contribute ? Fork this code, update and send-me a pull-request !!

Author: Sérgio Berlotto <sergio.berlotto {at} gmail.com>
