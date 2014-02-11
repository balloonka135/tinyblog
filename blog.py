#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from flask import Flask, url_for, render_template
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config["MONGODB_DB"] = "blog"
app.config["MONGODB_USERNAME"] = "db1"
app.config["MONGODB_PASSWORD"] = "db1"
app.config["MONGODB_HOST"] = "troup.mongohq.com"
app.config["MONGODB_PORT"] = 10012

app.config["SECRET_KEY"] = "KeepThisS3cr3th366e"

app.config["TEMPLATE_NAME"] = "default"

db = MongoEngine(app)

#================================================ MODELS
class Post(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    title = db.StringField(max_length=255, required=True)
    slug = db.StringField(max_length=255, required=True)
    body = db.StringField(required=True)
    comments = db.ListField(db.EmbeddedDocumentField('Comment'))

    def get_absolute_url(self):
        return url_for('post_detail', kwargs={"slug": self.slug})

    def __unicode__(self):
        return self.slug

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }


class Page(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    title = db.StringField(max_length=255, required=True)
    slug = db.StringField(max_length=255, required=True)
    body = db.StringField(required=True)

    def get_absolute_url(self):
        return url_for('page', kwargs={"slug": self.slug})

    def __unicode__(self):
        return self.slug

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }


class Comment(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    body = db.StringField(verbose_name="Comment", required=True)
    author = db.StringField(verbose_name="Name", max_length=255, required=True)


#================================================ VIEWS

@app.route("/")
def list_view():
    posts = Post.objects.all()
    pages = Page.objects.all()
    return render_template("%s/posts_list.html" % app.config.get("TEMPLATE_NAME") , posts=posts, pages=pages)


@app.route("/<slug>/")
def post_detail(slug):
    post = Post.objects.get_or_404(slug=slug)
    pages = Page.objects.all()
    return render_template("%s/post_detail.html" % app.config.get("TEMPLATE_NAME"), post=post, pages=pages, is_single=True)


@app.route("/page/<slug>/")
def page_detail(slug):
    page = Page.objects.get_or_404(slug=slug)
    pages = Page.objects.all()
    return render_template("%s/page_detail.html" % app.config.get("TEMPLATE_NAME"), page=page, pages=pages, is_single=True, is_page=True)


if __name__ == '__main__':
    app.run()
