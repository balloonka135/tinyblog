#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from flask import Flask, url_for, render_template, request, redirect
from flask.ext.mongoengine import MongoEngine
from flask.ext.mongoengine.wtf import model_form
from flask.ext.superadmin import Admin, model

app = Flask(__name__)
app.config["MONGODB_DB"] = "blog"
app.config["MONGODB_USERNAME"] = "db1"
app.config["MONGODB_PASSWORD"] = "db1"
app.config["MONGODB_HOST"] = "troup.mongohq.com"
app.config["MONGODB_PORT"] = 10012

app.config["SECRET_KEY"] = "KeepThisS3cr3th366e"

app.config["TEMPLATE_NAME"] = "default"

db = MongoEngine(app)

admin = Admin(app, name="TinyBlog")

#================================================ MODELS
class Page(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    title = db.StringField(max_length=255, required=True)
    slug = db.StringField(max_length=255, required=True)

    def get_absolute_url(self):
        return url_for('page', kwargs={"slug": self.slug})

    def __unicode__(self):
        return self.slug

    @property
    def post_type(self):
        return self.__class__.__name__

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }


class Post(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    title = db.StringField(max_length=255, required=True)
    slug = db.StringField(max_length=255, required=True)
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


class BlogPost(Post):
    body = db.StringField(required=True)


class Video(Post):
    embed_code = db.StringField(required=True)


class Image(Post):
    image_url = db.StringField(required=True, max_length=255)


class Quote(Post):
    body = db.StringField(required=True)
    author = db.StringField(verbose_name="Author Name", required=True, max_length=255)


class Comment(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    body = db.StringField(verbose_name="Comment", required=True)
    author = db.StringField(verbose_name="Name", max_length=255, required=True)


#================================================ ADMIN VIEWS

class PostModel(model.ModelAdmin):
    # fields = ("title","slug","body")
    list_display = ('title','created_at')
    # only = ('username',)
    exclude = ('created_at',)
    search_fields = ('title', 'created_at')

admin.register(BlogPost, PostModel)

#================================================ VIEWS

make_form = model_form(Comment, exclude=['created_at'])

@app.route("/")
def list_view():
    posts = Post.objects.all()
    pages = Page.objects.all()
    return render_template("%s/posts_list.html" % app.config.get("TEMPLATE_NAME") , posts=posts, pages=pages)


@app.route("/<int:page>/")
def list_view_page(page):
    posts = Post.objects.all()
    pages = Page.objects.all()
    return render_template("%s/posts_list.html" % app.config.get("TEMPLATE_NAME") , posts=posts, pages=pages)


@app.route("/<slug>/", methods=("GET",))
def post_detail(slug):
    post = Post.objects.get_or_404(slug=slug)
    pages = Page.objects.all()
    form = make_form(request.form)
    return render_template("%s/post_detail.html" % app.config.get("TEMPLATE_NAME"), post=post, pages=pages, form=form, is_single=True)


@app.route('/<slug>/', methods=("POST",))
def save_post(slug):
    post = Post.objects.get_or_404(slug=slug)
    form = make_form(request.form)

    if form.validate():
        comment = Comment()
        form.populate_obj(comment)

        post.comments.append(comment)
        post.save()

        return redirect(url_for('post_detail', slug=slug))

    pages = Page.objects.all()
    return render_template("%s/post_detail.html" % app.config.get("TEMPLATE_NAME"), post=post, pages=pages, form=form, is_single=True)

@app.route("/page/<slug>/")
def page_detail(slug):
    page = Page.objects.get_or_404(slug=slug)
    pages = Page.objects.all()
    return render_template("%s/page_detail.html" % app.config.get("TEMPLATE_NAME"), page=page, pages=pages, is_single=True, is_page=True)


if __name__ == '__main__':
    app.run()
