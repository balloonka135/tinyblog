#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import os.path as op
import wtforms

from flask import Flask, url_for, render_template, request, redirect, make_response, abort
from flask.ext.mongoengine import MongoEngine
from flask.ext import admin, wtf
from flask.ext.admin.form import rules
from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin


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

admin = admin.Admin(app, 'TinyBlog Admin')

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
class CKTextAreaWidget(wtforms.widgets.TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(wtforms.fields.TextAreaField):
    widget = CKTextAreaWidget()


class BaseAdminView(ModelView):
    column_filters = ['title', 'created_at','enable_comments']
    column_searchable_list = ('title','slug')
    # form_overrides = dict(enable_comments=wtforms.fields.SelectField)
    # form_args = dict(
    #     enable_comments=dict(
    #         choices=[(True, True), (False, False)]
    #     ))

class PostView(BaseAdminView):
    column_searchable_list = ('title','slug','body')
    form_create_rules = ('title', 'body', 'slug', 'tags', 'created_at', 'enable_comments')
    form_overrides = dict( body=CKTextAreaField)
    # form_overrides = dict(enable_comments=wtforms.fields.SelectField, body=CKTextAreaField)
    create_template = 'admin/edit.html'
    edit_template = 'admin/edit.html'

class VideoView(BaseAdminView):
    column_searchable_list = ('title','slug','embed_code')

class ImageView(BaseAdminView):
    pass

class QuoteView(BaseAdminView):
    column_searchable_list = ('title','slug','body','author')

admin.add_view(PostView(Post, endpoint="post", category=u'Conteúdo'))
admin.add_view(VideoView(Video, endpoint="video", category=u'Conteúdo'))
admin.add_view(ImageView(Image, endpoint="image", category=u'Conteúdo'))
admin.add_view(QuoteView(Quote, endpoint="quote", category=u'Conteúdo'))

path = op.join(op.dirname(__file__), 'static/uploads')
admin.add_view(FileAdmin(path, '/static/uploads/', name='Media Files'))

#================================================ VIEWS
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/")
def index():
    posts = PostBase.objects.all()
    return render_template("posts_list.html" , posts=posts)

@app.route("/tag/<tag>/")
def list_view_tag(tag):
    t_search = Tag.objects(name=tag).first()
    if not t_search:
        return abort(404)
    posts = PostBase.objects(tags=t_search)
    return render_template("posts_list.html", posts=posts)

@app.route('/image/<slug>/')
def image_view(slug):
    post = Image.objects.get_or_404(slug=slug)
    response=make_response( post.image.read() )
    response.headers['Content-Type'] = post.image.content_type
    return response

@app.route("/<int:page>/")
def list_view_page(page):
    posts = PostBase.objects.all()
    return render_template("posts_list.html", posts=posts)


@app.route("/<slug>/", methods=("GET",))
def post_detail(slug):
    post = PostBase.objects.get_or_404(slug=slug)
    return render_template("post_detail.html", post=post, is_single=True)


if __name__ == '__main__':
    app.run()
