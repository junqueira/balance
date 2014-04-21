import os
from flask import Flask
import os

# app = Flask(__name__)

# @app.route('/')
# def hello():
#     return 'Hello World!'

# if __name__ == "__main__":
#     app.run()

# def index(request):
#     r = requests.get('http://httpbin.org/status/418')
#     times = int(os.environ.get('TIMES',3))
#     print(r.text)
#     return HttpResponse('<pre>' + r.text + '</pre>')

# def db(request):
#     greeting = Greeting()
#     greeting.save()
#     greetings = Greeting.objects.all()
#     return render(request, 'db.html', {'greetings': greetings})

from datetime import datetime
import hashlib
from markdown import markdown
import bleach
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import request, current_app
from flask.ext.login import UserMixin
from . import db, login_manager


# class User(UserMixin, models.Model):  #db.Model):
#     #__tablename__ = 'users'
#     #id = db.Column(db.Integer, primary_key=True)
#     email = models.CharField(max_length=100)      #db.Column(db.String(64), nullable=False, unique=True, index=True)
#     username = models.CharField(max_length=100)   #db.Column(db.String(64), nullable=False, unique=True, index=True)
#     is_admin = models.BooleanField(default=True, db_index=True)  #db.Column(db.Boolean)
#     password_hash = models.CharField(max_length=100)   #db.Column(db.String(128))
#     name = models.CharField(max_length=100)            #db.Column(db.String(64))
#     location = models.CharField(max_length=100)        #db.Column(db.String(64))
#     bio = models.CharField(max_length=100)             #db.Column(db.Text())
#     member_since = models.DateField('date last purchase') #db.Column(db.DateTime(), default=datetime.utcnow)
#     avatar_hash = models.CharField(max_length=100)        #db.Column(db.String(32))
#     #talks = db.relationship('Talk', lazy='dynamic', backref='author')
#     #comments = db.relationship('Comment', lazy='dynamic', backref='author')

class User(UserMixin, db.Model):
    __tablename__ = 'finance_user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True, index=True)
    username = db.Column(db.String(64), nullable=False, unique=True, index=True)
    is_admin = db.Column(db.Boolean)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    bio = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    #talks = db.relationship('Talk', lazy='dynamic', backref='author')
    #comments = db.relationship('Comment', lazy='dynamic', backref='author')


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or \
               hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def for_moderation(self, admin=False):
        if admin and self.is_admin:
            return Comment.for_moderation()
        return Comment.query.join(Talk, Comment.talk_id == Talk.id).\
            filter(Talk.author == self).filter(Comment.approved == False)

    def get_api_token(self, expiration=300):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'user': self.id}).decode('utf-8')

    @staticmethod
    def validate_api_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        id = data.get('user')
        if id:
            return User.query.get(id)
        return None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# class Talk(models.Model):    #db.Model):
#     #__tablename__ = 'talks'
#     #id = db.Column(db.Integer, primary_key=True)
#     title = models.CharField(max_length=100)           #db.Column(db.String(128), nullable=False)
#     description = models.CharField(max_length=100)     #db.Column(db.Text)
#     slides = models.CharField(max_length=100)          #db.Column(db.Text())
#     video = models.CharField(max_length=100)           #db.Column(db.Text())
#     user_id = models.DecimalField(max_digits=8, decimal_places=2) #db.Column(db.Integer, db.ForeignKey('users.id'))
#     venue = models.CharField(max_length=100)           #db.Column(db.String(128))
#     venue_url = models.CharField(max_length=100)       #db.Column(db.String(128))
#     date = models.DateField('date last purchase')      #db.Column(db.DateTime())
#     #comments = db.relationship('Comment', lazy='dynamic', backref='talk')
#     #emails = db.relationship('PendingEmail', lazy='dynamic', backref='talk')

class Talk(db.Model):
    __tablename__ = 'finance_talk'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    slides = db.Column(db.Text())
    video = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    venue = db.Column(db.String(128))
    venue_url = db.Column(db.String(128))
    date = db.Column(db.DateTime())
    #comments = db.relationship('Comment', lazy='dynamic', backref='talk')
    #emails = db.relationship('PendingEmail', lazy='dynamic', backref='talk')

    def approved_comments(self):
        return self.comments.filter_by(approved=True)

    def get_unsubscribe_token(self, email, expiration=604800):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'talk': self.id, 'email': email}).decode('utf-8')

    @staticmethod
    def unsubscribe_user(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None, None
        id = data.get('talk')
        email = data.get('email')
        if not id or not email:
            return None, None
        talk = Talk.query.get(id)
        if not talk:
            return None, None
        Comment.query\
            .filter_by(talk=talk).filter_by(author_email=email)\
            .update({'notify': False})
        db.session.commit()
        return talk, email


# class Comment(models.Model):   #db.Model):
#     #__tablename__ = 'comments'
#     #id = db.Column(db.Integer, primary_key=True)
#     body = models.CharField(max_length=100)             #db.Column(db.Text)
#     body_html = models.CharField(max_length=100)        #db.Column(db.Text)
#     timestamp =  models.DateField('date last purchase')             #db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     author_id = models.DecimalField(max_digits=8, decimal_places=2) #db.Column(db.Integer, db.ForeignKey('users.id'))
#     author_name = models.CharField(max_length=100)                  #db.Column(db.String(64))
#     author_email = models.CharField(max_length=100)                 #db.Column(db.String(64))
#     notify = models.BooleanField(default=True, db_index=True)       #db.Column(db.Boolean, default=True)
#     approved = models.BooleanField(default=True, db_index=True)     #db.Column(db.Boolean, default=False)
#     talk_id = models.DecimalField(max_digits=8, decimal_places=2)   #db.Column(db.Integer, db.ForeignKey('talks.id'))

class Comment(db.Model):
    __tablename__ = 'finance_comment'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author_name = db.Column(db.String(64))
    author_email = db.Column(db.String(64))
    notify = db.Column(db.Boolean, default=True)
    approved = db.Column(db.Boolean, default=False)
    talk_id = db.Column(db.Integer, db.ForeignKey('talks.id'))


    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    @staticmethod
    def for_moderation():
        return Comment.query.filter(Comment.approved == False)

    def notification_list(self):
        list = {}
        for comment in self.talk.comments:
            # include all commenters that have notifications enabled except
            # the author of the talk and the author of this comment
            if comment.notify and comment.author != comment.talk.author:
                if comment.author:
                    # registered user
                    if self.author != comment.author:
                        list[comment.author.email] = comment.author.name or \
                                                     comment.author.username
                else:
                    # regular user
                    if self.author_email != comment.author_email:
                        list[comment.author_email] = comment.author_name
        return list.items()


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


# class PendingEmail(models.Model):    #db.Model):
#     #__tablename__ = 'pending_emails'
#     #id = db.Column(db.Integer, primary_key=True)
#     name = models.CharField(max_length=100)                #db.Column(db.String(64))
#     email = models.CharField(max_length=100)               #db.Column(db.String(64), index=True)
#     subject = models.CharField(max_length=100)             #db.Column(db.String(128))
#     body_text = models.CharField(max_length=100)           #db.Column(db.Text())
#     body_html = models.CharField(max_length=100)           #db.Column(db.Text())
#     talk_id = models.DecimalField(max_digits=8, decimal_places=2)  #db.Column(db.Integer, db.ForeignKey('talks.id'))
#     timestamp = models.DateField('date last purchase')     #db.Column(db.DateTime, index=True, default=datetime.utcnow)

class PendingEmail(db.Model):
    __tablename__ = 'pending_emails'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64), index=True)
    subject = db.Column(db.String(128))
    body_text = db.Column(db.Text())
    body_html = db.Column(db.Text())
    talk_id = db.Column(db.Integer, db.ForeignKey('talks.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def already_in_queue(email, talk):
        return PendingEmail.query\
            .filter(PendingEmail.talk_id == talk.id)\
            .filter(PendingEmail.email == email).count() > 0

    @staticmethod
    def remove(email):
        PendingEmail.query.filter_by(email=email).delete()


