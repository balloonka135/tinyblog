#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import os.path as op
import wtforms
import os

from flask import Flask, url_for, render_template, request, redirect, make_response, abort, flash, g, session
from flask.ext.mongoengine import MongoEngine
from flask.ext import admin, wtf
from flask.ext.paginate import Pagination
from flask.ext.wtf import Form
from flask.ext.admin import helpers, expose
from flask.ext.admin.form import rules
from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

#======================================================== SOME VARIABLES
ROLE_USER = 0
ROLE_ADMIN = 1
basedir = op.dirname(__file__)
#========================================================

app = Flask(__name__)

app.config["DEBUG"] = True
# app.config["MONGODB_DB"] = "blog"
# app.config["MONGODB_USERNAME"] = "db1"
# app.config["MONGODB_PASSWORD"] = "db1"
# app.config["MONGODB_HOST"] = "troup.mongohq.com"
# app.config["MONGODB_PORT"] = 10012

app.config["MONGODB_DB"] = "blog"
app.config["MONGODB_USERNAME"] = "db1"
app.config["MONGODB_PASSWORD"] = "db1"
app.config["MONGODB_HOST"] = "10.0.33.34"
# app.config["MONGODB_PORT"] = 10012

app.config["SECRET_KEY"] = "KeepThisS3cr3th366e"

app.config["SITE_TITLE"] = "PythonRS"
app.config["SITE_SUBTITLE"] = "Programando Python no Rio Grande do Sul"
app.config["POSTS_PER_PAGE"] = 7

db = MongoEngine(app)

lm = LoginManager()
lm.init_app(app)

# Create customized index view class
class AuthAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return super(AuthAdminIndexView, self).index()


    @expose('/login', methods = ['GET', 'POST'])
    def login_view(self):

        form = LoginForm(request.form)
        if request.method == 'POST' and form.validate():
            user = form.get_user()
            login_user(user)
            return redirect(url_for('index'))

        return render_template('auth_form.html', form=form)


    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if request.method == 'POST' and form.validate():
            user = User()

            form.populate_obj(user)
            user.save()

            login_user(user)
            return redirect(url_for('index'))

        return render_template('auth_form.html', form=form)

    @expose('/logout')
    def logout(self):
        logout_user()
        return redirect(url_for('index'))


    # def is_accessible(self):
    #     return current_user.is_authenticated()


admin = admin.Admin(app, 'TinyBlog Admin', index_view=AuthAdminIndexView(url='/admin', name='Admin Home'))

#================================================ MODELS
class Tag(db.Document):
    name = db.StringField(max_length=20)

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


class User(db.Document):
    login = db.StringField(max_length=80, unique=True, required = True)
    email = db.StringField(max_length=120, unique = True)
    role = db.IntField(default = ROLE_USER)
    password = db.StringField(max_length=64)
    posts = db.ListField(db.ReferenceField(Post))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.login)


#================================================ ADMIN VIEWS
class CKTextAreaWidget(wtforms.widgets.TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(wtforms.fields.TextAreaField):
    widget = CKTextAreaWidget()


# Create customized model view class
class AuthModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated()


class BaseAdminView(AuthModelView):
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
    column_list = ('title', 'created_at',"enable_comments","tags")
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
admin.add_view(AuthModelView(Tag, endpoint="tag", category=u'Conteúdo'))


path = op.join(op.dirname(__file__), 'static/uploads')
admin.add_view(FileAdmin(path, '/static/uploads/', name='Media Files'))

#================================================ LOGINS
# Define login and registration forms (for flask-login)
class LoginForm(Form):
    login = wtforms.fields.TextField(validators=[wtforms.validators.required()])
    password = wtforms.fields.PasswordField(validators=[wtforms.validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise wtforms.validators.ValidationError('Invalid user')

        if user.password != self.password.data:
            raise wtforms.validators.ValidationError('Invalid password')

    def get_user(self):
        return User.objects(login=self.login.data).first()

class RegistrationForm(Form):
    login = wtforms.fields.TextField(validators=[wtforms.validators.required()])
    email = wtforms.fields.TextField()
    password = wtforms.fields.PasswordField(validators=[wtforms.validators.required()])

    def validate_login(self, field):
        if User.objects(login=self.login.data):
            raise wtforms.validators.ValidationError('Duplicate username')

@lm.user_loader
def load_user(id):
    return User.objects.get(id=id)

@app.before_request
def before_request():
    g.user = current_user


#================================================ VIEWS
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/")
@app.route("/page/<int:page>")
def index(page=1):
    user = g.user
    perpage = int(app.config["POSTS_PER_PAGE"])
    total = PostBase.objects.count()
    # pages_total = round((float(total)/float(perpage))+.5)
    pages_total = round(total/perpage)
    posts = PostBase.objects.skip((int(page)-1)*perpage).limit(perpage)
    pagination = Pagination(page=page, total=total, per_page=perpage, css_framework='bootstrap',
        bs_version=3, record_name="Posts")
    return render_template("posts_list.html" , posts=posts, total=total, page=page,
        pages=int(pages_total), user=user, pagination=pagination)


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
