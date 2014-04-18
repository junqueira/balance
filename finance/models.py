from django.db import models
from datetime import datetime
from django.contrib.contenttypes.models import *
#from finance.worksheet import WorkSheet
import gspread
import os
from django.conf import settings


class TypeLaunch(models.Model):
    type_name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return u'%s' % (self.type_name)


class Provider(models.Model):
    description = models.CharField(max_length=100, unique=True)
    type_launch = models.ForeignKey(TypeLaunch, blank=True, null=True)
    date_last_purchase = models.DateField('date last purchase')
    value_total = models.DecimalField(max_digits=8, decimal_places=2)

    def update(self, launch):
        provider = Provider.objects.get(description=launch)
        provider.date_last_purchase = self.date_last_purchase
        provider.value_total = self.value_total
        provider.save()


class Extract(models.Model):
	date_launch = models.DateField('date launch')
	launch = models.CharField(max_length=100)
	date_purchase = models.DateField('date purchase')
	value_debit = models.DecimalField(max_digits=8, decimal_places=2)
	value_credit = models.DecimalField(max_digits=8, decimal_places=2)
	value_balance = models.DecimalField(max_digits=8, decimal_places=2)
	cancelled = models.BooleanField(default=True, db_index=True)

	DayL = ['Mon', 'Tues', 'Wednes', 'Thurs', 'Fri', 'Satur', 'Sun']

	def dif_date(self, date, day):
		return date.fromordinal(date.toordinal()-day)

	def set_cost(self, cost):
		_type = TypeLaunch.objects.all()
		for t in _type:
			print("Codigo = " + str(t.id) + " type = " + t.type_name)
		desc = 'Inform the cost type to: ' + cost.launch
		desc += ' value last purchase ' + str(cost.value_debit) + " => "
		n = input(desc)
		while not TypeLaunch.objects.filter(id=n).exists():
			n = input(desc)
		prov = Provider.objects.get(description=cost.launch)
		prov.type_launch_id = n
		prov.save()

	def get_cost(self, cost):
		prov = Provider.objects.get(description=cost.launch)
		_type = TypeLaunch.objects.get(id=prov.type_launch_id)
		return _type.type_name

	def print_launch(self, date):
		extract = Extract.objects.filter(date_purchase=date)
		cust_day = 0
		cust_total = 0
		for cost in extract:
			prov = Provider.objects.filter(description=cost.launch)
			if prov.exists() and prov[0].type_launch_id is None:
				self.set_cost(cost)
			else:
				cust_day += cost.value_debit
				desc = ' # ' + str(cost.launch) + ' => ' + str(cost.value_debit)
				desc += ' => ' + self.get_cost(cost)
				print(desc)
		print(' ## ' + str(cust_day) + ' ## ')

	def get_week(self):
		date = datetime.today().date()
		num_w = date.weekday()

	def report_week(self, date=''):
		extract = Extract()
		extract.importer()
		date = datetime.today().date()
		#date = datetime.strptime('25-10-2014', '%d-%m-%Y').date()
		fri = 4
		n = 0
		week = date.weekday()
		first_day_week = self.dif_date(date, week)

		last_date_purchase = Extract.objects.all().last().date_purchase
		# print('primeiro dia = ' + str(first_day_week) + 'ultimo lanca = ' + str(last_date_purchase) )
		# if first_day_week > last_date_purchase:
		# 	print('Weeks earlier not closed, archive extract is old')
		# else:
		while n < 7:
			# the weekly cost and so closed 'Fri', 'Satur' or 'Sun
			if week < fri:
				day = self.dif_date(date, 7 + week - n)
			else:
				day = self.dif_date(date, week - n)
			print(str(day) + ' => ' + self.DayL[n] + 'day')

			self.print_launch(day)
			self.send(day)
			n += 1

	def str_to_date(self, date_launch):
		date = date_launch.replace('/','-')
		return datetime.strptime(date, '%d-%m-%Y').date()

	def get_date_purchase(self, date, launch):
		launch = launch.strip()
		if launch[-3] == '/':
			date_purchase = launch[-5:].replace('/','-')
			date = date_purchase + '-' + str(date.year)
			date = datetime.strptime(date, '%d-%m-%Y').date()
		return date

	def str_to_float(self, value):
		value = float(value.replace(',','.'))
		return float("{0:.2f}".format(round(value,2)))

	def is_equal(self, date_launch, launch, value):
		if value < 0:
			t = Extract.objects.filter(date_launch=date_launch, launch=launch, value_debit=abs(value))
		else:
			t = Extract.objects.filter(date_launch=date_launch, launch=launch, value_credit=value)
		return t

	def get_launch(self, launch):
		launch = launch.strip()
		if launch[-3] == '/':
			launch = launch[:-6].strip()
		return launch

	def get_value_total(self, launch):
		total = 0
		for value in Extract.objects.filter(launch=launch):
			if value.value_debit > 0:
				total += value.value_debit
			else:
				total += value.value_credit
		return total

	def provider(self, launch):
		#import pdb; pdb.set_trace()
		provider = Provider()
		provider.description = launch
		provider.date_last_purchase = Extract.objects.filter(launch=launch).last().date_purchase
		provider.value_total = self.get_value_total(launch)

		if not Provider.objects.filter(description=launch).exists():
			provider.save()
		else:
			provider.update(launch)

	def importer(self, path=''):
		path = os.path.expanduser("~") + "/Downloads/extrato.txt"

		with open(path, 'r') as ff:
			contents = ff.readlines()
			line = 0
			while line < len(contents):
				extract = Extract()
				date_launch, launch, value = contents[line].split(';')
				date_launch = extract.str_to_date(date_launch)
				date_purchase = extract.get_date_purchase(date_launch, launch)
				value = extract.str_to_float(value)
				launch = extract.get_launch(launch)

				if not extract.is_equal(date_launch, launch, value).exists():
					extract.date_launch = date_launch
					extract.launch = launch
					extract.date_purchase = date_purchase

					if value < 0:
						extract.value_debit = abs(value)
						extract.value_credit = 0
					else:
						extract.value_debit = 0
						extract.value_credit = value

					extract.value_balance = 0
					extract.save()

				extract.provider(launch)
				line += 1

			ff.close()

	def send(self, date):
		#date = datetime.strptime('17-10-2014' , '%d-%m-%Y').date()
		g = gspread.login(settings.EMAIL_GOOGLE, settings.SENHA_GOOGLE)
		g.open_by_key(settings.DOC_KEY_GOOGLE)
		sh = g.open("cost_week")
		#worksheet = sh.get_worksheet(0)
		name_worksheet = "Week - " + str(date.isocalendar()[1])
		try:
			worksheet = sh.add_worksheet(title=name_worksheet, rows="40", cols="32")
		except Exception:
			worksheet = sh.worksheet("Week - " + str(date.isocalendar()[1]))

		#worksheet.update_acell('B1', 'Bingo!')
		#worksheet.update_cell(1, 2, 'Bingo!')
		#cell_list = worksheet.range('A1:C7')
		extract = Extract.objects.filter(date_purchase=date)
		coll = (date.weekday()+1) * 4
		day_cost = 0
		for launch in extract:
			day_cost += launch.value_debit

		day_name = self.DayL[date.weekday()]
		worksheet.update_cell(1, coll, day_name)
		worksheet.update_cell(1, coll+1, str(day_cost).replace('.',','))
		worksheet.update_cell(1, coll+2, 'Type')
		line = 2
		for cost in extract:
			worksheet.update_cell(line, coll, cost.launch)
			worksheet.update_cell(line, coll+1, str(cost.value_debit).replace('.',','))
			worksheet.update_cell(line, coll+2, self.get_cost(cost))
			line += 1

		# for x in extract:
		#     total += x.value_debit
		#     print(' # ' + str(x.launch) + ' => ' + str(x.value_debit))
		# print(' ## ' + str(total) + ' ## ')

		# for cell in cell_list:
		#   cell.value = 'O_o'

		# worksheet.update_cells(cell_list)


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
    name = db.Column(db.String(64), nullable=False, unique=True, index=True)
    location = db.Column(db.String(64))
    bio = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.today().date())
    avatar_hash = db.Column(db.String(32))
    #talks = db.relationship('Talk', lazy='dynamic', backref='author')
    #comments = db.relationship('Comment', lazy='dynamic', backref='author')


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        self.name = self.username
        self.location = self.username
        self.bio = self.username
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
        # return Comment.query.join(Talk, Comment.talk_id == Talk.id).\
        #     filter(Talk.author == self).filter(Comment.approved == False)

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
    #user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
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
    #author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author_name = db.Column(db.String(64))
    author_email = db.Column(db.String(64))
    notify = db.Column(db.Boolean, default=True)
    approved = db.Column(db.Boolean, default=False)
    #talk_id = db.Column(db.Integer, db.ForeignKey('talks.id'))


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
    #talk_id = db.Column(db.Integer, db.ForeignKey('talks.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # @staticmethod
    # def already_in_queue(email, talk):
    #     return PendingEmail.query\
    #         .filter(PendingEmail.talk_id == talk.id)\
    #         .filter(PendingEmail.email == email).count() > 0

    @staticmethod
    def remove(email):
        PendingEmail.query.filter_by(email=email).delete()


