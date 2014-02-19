#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import os.path as op

from flask import Flask, url_for, render_template, request, redirect, make_response
from flask.ext.mongoengine import MongoEngine
from flask.ext.superadmin import Admin, model

app = Flask(__name__)
app.config["MONGODB_DB"] = "blog"
app.config["MONGODB_USERNAME"] = "db1"
app.config["MONGODB_PASSWORD"] = "db1"
app.config["MONGODB_HOST"] = "troup.mongohq.com"
app.config["MONGODB_PORT"] = 10012

app.config["SECRET_KEY"] = "KeepThisS3cr3th366e"

app.config["TEMPLATE_NAME"] = "default"
app.config["SITE_TITLE"] = "PythonRS"
app.config["SITE_SUBTITLE"] = "Programando Python no Rio Grande do Sul"
app.config["POSTS_PER_PAGE"] = 7

db = MongoEngine(app)

admin = Admin(app, name="TinyBlog")

#================================================ MODELS
class Tag(db.Document):
    name = db.StringField(max_length=10)

    def __unicode__(self):
        return self.name

class PostBase(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    title = db.StringField(max_length=255, required=True)
    slug = db.StringField(max_length=255, required=True)
    tags = db.ListField(db.ReferenceField('Tag'))
    enable_comments = db.BooleanField(default=False)

    def get_absolute_url(self):
        return url_for('post_detail', slug = self.slug)

    def __unicode__(self):
        return self.slug

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }


class Post(PostBase):
    body = db.StringField(required=True)


class Video(PostBase):
    embed_code = db.StringField(required=True)


class Image(PostBase):
    image = db.ImageField(thumbnail_size=(100, 100, True))


class Quote(PostBase):
    body = db.StringField(required=True)
    author = db.StringField(verbose_name="Author Name", required=True, max_length=255)


#================================================ ADMIN VIEWS

class PostModel(model.ModelAdmin):
    list_display = ('title','created_at', 'get_absolute_url')
    # only = ('username',)
    exclude = ('created_at','meta')
    search_fields = ('title', 'created_at')


admin.register(Tag)
admin.register(Post, PostModel)
admin.register(Video, PostModel)
admin.register(Image, PostModel)
admin.register(Quote, PostModel)

#================================================ VIEWS

@app.route("/")
def list_view():
    posts = PostBase.objects.all()
    return render_template("%s/posts_list.html" % app.config.get("TEMPLATE_NAME") , posts=posts)


@app.route('/image/<slug>/')
def image_view(slug):
    post = Image.objects.get_or_404(slug=slug)
    response=make_response( post.image.read() )
    response.headers['Content-Type'] = post.image.content_type
    return response

@app.route("/<int:page>/")
def list_view_page(page):
    posts = PostBase.objects.all()
    return render_template("%s/posts_list.html" % app.config.get("TEMPLATE_NAME") , posts=posts)


@app.route("/<slug>/", methods=("GET",))
def post_detail(slug):
    post = PostBase.objects.get_or_404(slug=slug)
    return render_template("%s/post_detail.html" % app.config.get("TEMPLATE_NAME"), post=post, is_single=True)


if __name__ == '__main__':
    app.run()
