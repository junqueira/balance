from django.db import models
from datetime import datetime
from django.contrib.contenttypes.models import *
#from finance.worksheet import WorkSheet
import gspread
import os
from django.conf import settings


class TypeLaunch(models.Model):
    type_name = models.CharField(max_length=100, unique=True)
    cost_fixo = models.BooleanField(default=False, db_index=True)

    def __unicode__(self):
        return u'%s' % (self.type_name)


class WeekNumber(models.Model):
		num_week = models.IntegerField()
		date_init = models.DateField('date initial week')
		date_final = models.DateField('date final week')

		def week_update(self, date=""):
			#date = datetime.today().date()
			n = 0
			num_week = date.isocalendar()[1]
			if not WeekNumber.objects.filter(num_week=num_week).exists():
				week = []
				while n < 7:
					week.append(self.dif_date(date, date.weekday() - n))
					n += 1
				wd = WeekNumber()
				wd.num_week = num_week
				wd.date_init = week[0]
				wd.date_final = week[6]
				wd.save()

		def dif_date(self, date, day):
			return date.fromordinal(date.toordinal()-day)


class Provider(models.Model):
		description = models.CharField(max_length=100, unique=True)
		date_last_purchase = models.DateField('date last purchase')
		total_debit_week = models.DecimalField(max_digits=8, decimal_places=2)
		total_credit_week = models.DecimalField(max_digits=8, decimal_places=2)
		type_launch = models.ForeignKey(TypeLaunch, blank=True, null=True)
		num_week = models.ForeignKey(WeekNumber, blank=True, null=True)

		def provider_update(self, launch, date):
			#launch = "RSHOP-CASA DO NOR"
			#date = datetime.strptime('19-11-2014', '%d-%m-%Y').date()
			if not Provider.objects.filter(description=launch).exists():
				pv = Provider()
			else:
				pv = Provider.objects.get(description=launch)
			pv.description = launch
			pv.date_last_purchase = date
			num_week = date.isocalendar()[1]
			week = WeekNumber.objects.filter(num_week=num_week)
			if not week.exists():
				wn = WeekNumber()
				wn.week_update(date)

			tot_debit = 0
			tot_credit = 0
			pv_week = Extract.objects.filter(launch=launch, date_purchase__range=[week.first().date_init, week.first().date_final])
			for value in pv_week:
				if value.value_debit > 0:
					tot_debit += value.value_debit
				if value.value_credit >0:
					tot_credit += value.value_credit

			pv.total_debit_week = tot_debit
			pv.total_credit_week = tot_credit
			if pv.type_launch_id is None:
				pv.type_launch_id  = self.set_provider_type(pv)
			pv.num_week_id = num_week
			pv.save()

		def set_provider_type(self, pv):
			_type = TypeLaunch.objects.all()
			for t in _type:
				print("Codigo = " + str(t.id) + " type = " + t.type_name)
			desc = 'Inform type to: ' + pv.description
			name_day = Extract.DayL[pv.date_last_purchase.weekday()] + " day " + str(pv.date_last_purchase.day) + " " + pv.date_last_purchase.strftime("%B")
			desc += ' last date: ' + name_day
			desc += ' debit week: ' + str(pv.total_debit_week)
			desc += ' credit week: ' + str(pv.total_credit_week) + " => "
			n = input(desc)
			while not TypeLaunch.objects.filter(id=n).exists():
				n = input(desc)
			return n

		def get_type_launch(self, pv):
			_type = TypeLaunch.objects.get(id=prov.type_launch_id)
			return _type.type_name


class Extract(models.Model):
	date_launch = models.DateField('date launch')
	launch = models.CharField(max_length=100)
	date_purchase = models.DateField('date purchase')
	value_debit = models.DecimalField(max_digits=8, decimal_places=2)
	value_credit = models.DecimalField(max_digits=8, decimal_places=2)
	value_balance = models.DecimalField(max_digits=8, decimal_places=2)
	cancelled = models.BooleanField(default=True, db_index=True)

	DayL = ['Mon', 'Tues', 'Wednes', 'Thurs', 'Fri', 'Satur', 'Sun']

	def report_week(self, date=''):
		self.importer()
		date = datetime.today().date()
		num_week = date.isocalendar()[1]
		week = self.get_week(date)
		for day in week:
			if day.weekday() == 0:
				worksheet = self.get_worksheet(day)
			#self.send_cost_week(worksheet, day)

	# def print_launch(self, date):
	# 	extract = Extract.objects.filter(date_purchase=date)
	# 	cust_day = 0
	# 	print(str(date) + ' => ' + self.DayL[date.weekday()] + 'day')
	# 	for ext in extract:
	# 		cust_day += ext.value_debit
	# 		desc = ' # ' + str(ext.launch) + ' => ' + str(ext.value_debit)
	# 		desc += ' => ' + self.get_cost(ext)
	# 		print(desc)
	# 	print(' ## ' + str(cust_day) + ' ## ')

	def get_worksheet(self, date):
			g = gspread.login(settings.EMAIL_GOOGLE, settings.SENHA_GOOGLE)
			g.open_by_key(settings.DOC_KEY_GOOGLE)
			sh = g.open("cost_week")
			name_worksheet = "Week - " + str(date.isocalendar()[1])
			rows = "40"
			cols = "32"
			try:
				worksheet = sh.add_worksheet(title=name_worksheet, rows=rows, cols=cols)
			except Exception:
				worksheet = sh.worksheet("Week - " + str(date.isocalendar()[1]))

			self.send_summary_week(worksheet, date)
			return worksheet

	def total_week(self, num_week, _type=None):
		value_week = []
		tot_debit_week = 0
		tot_credit_week = 0
		if _type is None:
			pv = Provider.objects.filter(num_week_id=num_week)
		else:
			pv = Provider.objects.filter(type_launch_id=_type, num_week_id=num_week)
		if pv.exists():
			for p in pv:
				tot_debit_week += p.total_debit_week
				tot_credit_week += p.total_credit_week
			value_week.append(tot_debit_week)
			value_week.append(tot_credit_week)
			value_week.append(tot_credit_week - tot_debit_week)
		return value_week

	def send_summary_week(self, worksheet, date):
		num_week = date.isocalendar()[1]
		tp_launch = TypeLaunch.objects.all()
		name_last_day = self.name_day(date.fromordinal(date.toordinal()+6))
		line = 1
		coll = 1
		worksheet.update_cell(line, coll, self.name_day(date))
		worksheet.update_cell(line, coll+1, "TO")
		worksheet.update_cell(line, coll+2, name_last_day)
		worksheet.update_cell(line, coll+3, "Account Itau")

		line = 2
		value_week = self.total_week(num_week)
		value_debit = value_week[0]
		value_credit = value_week[1]
		tot_week_before = self.total_week(num_week-1)[2] + self.total_week(num_week-2)[2]
		tot_week = tot_week_before - value_debit + value_credit
		if value_credit > value_debit:
			worksheet.update_cell(line, coll, "Result Positive")
		else:
			worksheet.update_cell(line, coll, "Result Negative")
		worksheet.update_cell(line, coll+1, str(value_debit).replace('.',','))
		worksheet.update_cell(line, coll+2, str(value_credit).replace('.',','))
		worksheet.update_cell(line, coll+3, str(tot_week).replace('.',','))

		line = 3
		worksheet.update_cell(line, coll, "Cost Week")
		worksheet.update_cell(line, coll+1, "Debit")
		worksheet.update_cell(line, coll+2, "Credit")
		worksheet.update_cell(line, coll+3, "Total")

		line = 4
		for tp in tp_launch:
			tot_week_type = self.total_week(num_week, tp.id)
			if len(tot_week_type):
				value_debit = str(tot_week_type[0]).replace('.',',')
				value_credit = str(tot_week_type[1]).replace('.',',')
				value_total = str(tot_week_type[2]).replace('.',',')
				worksheet.update_cell(line, coll, tp.type_name)
				worksheet.update_cell(line, coll+1, value_debit)
				worksheet.update_cell(line, coll+2, value_credit)
				worksheet.update_cell(line, coll+3, value_total)
				line += 1

	def name_day(self, date):
		name_day = self.DayL[date.weekday()] + " day " + str(date.day) + " " + date.strftime("%B")
		return name_day

	def send_cost_week(self, worksheet, week):
		extract = Extract.objects.filter(date_purchase=date)
		n_day = date.weekday()
		coll = (n_day+1) * 4
		day_cost = 0
		line = 2
		max_line = 0
		for launch in extract:
			day_cost += launch.value_debit

		day_name = self.name_day(date)
		worksheet.update_cell(1, coll, day_name)
		worksheet.update_cell(1, coll+1, str(day_cost).replace('.',','))
		worksheet.update_cell(1, coll+2, 'Type')
		for cost in extract:
			worksheet.update_cell(line, coll, cost.launch)
			worksheet.update_cell(line, coll+1, str(cost.value_debit).replace('.',','))
			worksheet.update_cell(line, coll+2, self.get_cost(cost))
			line += 1
			if max_line < line:
				max_line = line

		# cell_list = worksheet.range('A1:E15')
		# for cell in cell_list:
		# 	for cost in extract:
		# 		cell.value = cost.launch
		# 		cell.value = str(cost.value_debit).replace('.',',')
		# 		cell.value = self.get_cost(cost)
		# 		worksheet.update_cells(cell_list)

	def dif_date(self, date, day):
		return date.fromordinal(date.toordinal()-day)

	def get_week(self, date=""):
		#date = datetime.today().date()
		#date = datetime.strptime('28-11-2014', '%d-%m-%Y').date()
		num_w = date.weekday()
		week = []
		days = num_w + 7
		n = 0
		while n <= days:
			week.append(self.dif_date(date, days - n))
			n += 1
		return week

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
			#import ipdb; ipdb.set_trace()
			t = Extract.objects.filter(date_launch=date_launch, launch=launch, value_debit=abs(value))
		else:
			t = Extract.objects.filter(date_launch=date_launch, launch=launch, value_credit=value)
		return t

	def get_launch(self, launch):
		launch = launch.strip()
		if launch[-3] == '/':
			launch = launch[:-6].strip()
		return launch

	def importer(self, path=''):
		path = os.path.expanduser("~") + "/Downloads/extrato.txt"

		with open(path, 'r') as ff:
			contents = ff.readlines()
			line = 0
			while line < len(contents):
				extract = Extract()
				date_launch, launch, value = contents[line].split(';')
				date_launch = self.str_to_date(date_launch)
				date_purchase = self.get_date_purchase(date_launch, launch)
				value = self.str_to_float(value)
				launch = self.get_launch(launch)

				if not self.is_equal(date_launch, launch, value).exists():
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

				pv = Provider()
				pv.provider_update(launch, date_purchase)
				line += 1

			ff.close()
			print("Successfully imported file.")


# from datetime import datetime
# import hashlib
# from markdown import markdown
# import bleach
# from werkzeug.security import generate_password_hash, check_password_hash
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from flask import request, current_app
# from flask.ext.login import UserMixin
# from . import db, login_manager


# # class User(UserMixin, models.Model):  #db.Model):
# #     #__tablename__ = 'users'
# #     #id = db.Column(db.Integer, primary_key=True)
# #     email = models.CharField(max_length=100)      #db.Column(db.String(64), nullable=False, unique=True, index=True)
# #     username = models.CharField(max_length=100)   #db.Column(db.String(64), nullable=False, unique=True, index=True)
# #     is_admin = models.BooleanField(default=True, db_index=True)  #db.Column(db.Boolean)
# #     password_hash = models.CharField(max_length=100)   #db.Column(db.String(128))
# #     name = models.CharField(max_length=100)            #db.Column(db.String(64))
# #     location = models.CharField(max_length=100)        #db.Column(db.String(64))
# #     bio = models.CharField(max_length=100)             #db.Column(db.Text())
# #     member_since = models.DateField('date last purchase') #db.Column(db.DateTime(), default=datetime.utcnow)
# #     avatar_hash = models.CharField(max_length=100)        #db.Column(db.String(32))
# #     #talks = db.relationship('Talk', lazy='dynamic', backref='author')
# #     #comments = db.relationship('Comment', lazy='dynamic', backref='author')

# class User(UserMixin, db.Model):
#     __tablename__ = 'finance_user'
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(64), nullable=False, unique=True, index=True)
#     username = db.Column(db.String(64), nullable=False, unique=True, index=True)
#     is_admin = db.Column(db.Boolean)
#     password_hash = db.Column(db.String(128))
#     name = db.Column(db.String(64), nullable=False, unique=True, index=True)
#     location = db.Column(db.String(64))
#     bio = db.Column(db.Text())
#     member_since = db.Column(db.DateTime(), default=datetime.today().date())
#     avatar_hash = db.Column(db.String(32))
#     #talks = db.relationship('Talk', lazy='dynamic', backref='author')
#     #comments = db.relationship('Comment', lazy='dynamic', backref='author')


#     def __init__(self, **kwargs):
#         super(User, self).__init__(**kwargs)

#         self.name = self.username
#         self.location = self.username
#         self.bio = self.username
#         if self.email is not None and self.avatar_hash is None:
#             self.avatar_hash = hashlib.md5(
#                 self.email.encode('utf-8')).hexdigest()

#     @property
#     def password(self):
#         raise AttributeError('password is not a readable attribute')

#     @password.setter
#     def password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def verify_password(self, password):
#         return check_password_hash(self.password_hash, password)

#     def gravatar(self, size=100, default='identicon', rating='g'):
#         if request.is_secure:
#             url = 'https://secure.gravatar.com/avatar'
#         else:
#             url = 'http://www.gravatar.com/avatar'
#         hash = self.avatar_hash or \
#                hashlib.md5(self.email.encode('utf-8')).hexdigest()
#         return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
#             url=url, hash=hash, size=size, default=default, rating=rating)

#     def for_moderation(self, admin=False):
#         if admin and self.is_admin:
#             return Comment.for_moderation()
#         # return Comment.query.join(Talk, Comment.talk_id == Talk.id).\
#         #     filter(Talk.author == self).filter(Comment.approved == False)

#     def get_api_token(self, expiration=300):
#         s = Serializer(current_app.config['SECRET_KEY'], expiration)
#         return s.dumps({'user': self.id}).decode('utf-8')

#     @staticmethod
#     def validate_api_token(token):
#         s = Serializer(current_app.config['SECRET_KEY'])
#         try:
#             data = s.loads(token)
#         except:
#             return None
#         id = data.get('user')
#         if id:
#             return User.query.get(id)
#         return None


# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))


# # class Talk(models.Model):    #db.Model):
# #     #__tablename__ = 'talks'
# #     #id = db.Column(db.Integer, primary_key=True)
# #     title = models.CharField(max_length=100)           #db.Column(db.String(128), nullable=False)
# #     description = models.CharField(max_length=100)     #db.Column(db.Text)
# #     slides = models.CharField(max_length=100)          #db.Column(db.Text())
# #     video = models.CharField(max_length=100)           #db.Column(db.Text())
# #     user_id = models.DecimalField(max_digits=8, decimal_places=2) #db.Column(db.Integer, db.ForeignKey('users.id'))
# #     venue = models.CharField(max_length=100)           #db.Column(db.String(128))
# #     venue_url = models.CharField(max_length=100)       #db.Column(db.String(128))
# #     date = models.DateField('date last purchase')      #db.Column(db.DateTime())
# #     #comments = db.relationship('Comment', lazy='dynamic', backref='talk')
# #     #emails = db.relationship('PendingEmail', lazy='dynamic', backref='talk')

# class Talk(db.Model):
#     __tablename__ = 'finance_talk'
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(128), nullable=False)
#     description = db.Column(db.Text)
#     slides = db.Column(db.Text())
#     video = db.Column(db.Text())
#     #user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     venue = db.Column(db.String(128))
#     venue_url = db.Column(db.String(128))
#     date = db.Column(db.DateTime())
#     #comments = db.relationship('Comment', lazy='dynamic', backref='talk')
#     #emails = db.relationship('PendingEmail', lazy='dynamic', backref='talk')

#     def approved_comments(self):
#         return self.comments.filter_by(approved=True)

#     def get_unsubscribe_token(self, email, expiration=604800):
#         s = Serializer(current_app.config['SECRET_KEY'], expiration)
#         return s.dumps({'talk': self.id, 'email': email}).decode('utf-8')

#     @staticmethod
#     def unsubscribe_user(token):
#         s = Serializer(current_app.config['SECRET_KEY'])
#         try:
#             data = s.loads(token)
#         except:
#             return None, None
#         id = data.get('talk')
#         email = data.get('email')
#         if not id or not email:
#             return None, None
#         talk = Talk.query.get(id)
#         if not talk:
#             return None, None
#         Comment.query\
#             .filter_by(talk=talk).filter_by(author_email=email)\
#             .update({'notify': False})
#         db.session.commit()
#         return talk, email


# # class Comment(models.Model):   #db.Model):
# #     #__tablename__ = 'comments'
# #     #id = db.Column(db.Integer, primary_key=True)
# #     body = models.CharField(max_length=100)             #db.Column(db.Text)
# #     body_html = models.CharField(max_length=100)        #db.Column(db.Text)
# #     timestamp =  models.DateField('date last purchase')             #db.Column(db.DateTime, index=True, default=datetime.utcnow)
# #     author_id = models.DecimalField(max_digits=8, decimal_places=2) #db.Column(db.Integer, db.ForeignKey('users.id'))
# #     author_name = models.CharField(max_length=100)                  #db.Column(db.String(64))
# #     author_email = models.CharField(max_length=100)                 #db.Column(db.String(64))
# #     notify = models.BooleanField(default=True, db_index=True)       #db.Column(db.Boolean, default=True)
# #     approved = models.BooleanField(default=True, db_index=True)     #db.Column(db.Boolean, default=False)
# #     talk_id = models.DecimalField(max_digits=8, decimal_places=2)   #db.Column(db.Integer, db.ForeignKey('talks.id'))

# class Comment(db.Model):
#     __tablename__ = 'finance_comment'
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.Text)
#     body_html = db.Column(db.Text)
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     #author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     author_name = db.Column(db.String(64))
#     author_email = db.Column(db.String(64))
#     notify = db.Column(db.Boolean, default=True)
#     approved = db.Column(db.Boolean, default=False)
#     #talk_id = db.Column(db.Integer, db.ForeignKey('talks.id'))


#     @staticmethod
#     def on_changed_body(target, value, oldvalue, initiator):
#         allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
#                         'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
#                         'h1', 'h2', 'h3', 'p']
#         target.body_html = bleach.linkify(bleach.clean(
#             markdown(value, output_format='html'),
#             tags=allowed_tags, strip=True))

#     @staticmethod
#     def for_moderation():
#         return Comment.query.filter(Comment.approved == False)

#     def notification_list(self):
#         list = {}
#         for comment in self.talk.comments:
#             # include all commenters that have notifications enabled except
#             # the author of the talk and the author of this comment
#             if comment.notify and comment.author != comment.talk.author:
#                 if comment.author:
#                     # registered user
#                     if self.author != comment.author:
#                         list[comment.author.email] = comment.author.name or \
#                                                      comment.author.username
#                 else:
#                     # regular user
#                     if self.author_email != comment.author_email:
#                         list[comment.author_email] = comment.author_name
#         return list.items()


# db.event.listen(Comment.body, 'set', Comment.on_changed_body)


# # class PendingEmail(models.Model):    #db.Model):
# #     #__tablename__ = 'pending_emails'
# #     #id = db.Column(db.Integer, primary_key=True)
# #     name = models.CharField(max_length=100)                #db.Column(db.String(64))
# #     email = models.CharField(max_length=100)               #db.Column(db.String(64), index=True)
# #     subject = models.CharField(max_length=100)             #db.Column(db.String(128))
# #     body_text = models.CharField(max_length=100)           #db.Column(db.Text())
# #     body_html = models.CharField(max_length=100)           #db.Column(db.Text())
# #     talk_id = models.DecimalField(max_digits=8, decimal_places=2)  #db.Column(db.Integer, db.ForeignKey('talks.id'))
# #     timestamp = models.DateField('date last purchase')     #db.Column(db.DateTime, index=True, default=datetime.utcnow)

# class PendingEmail(db.Model):
#     __tablename__ = 'pending_emails'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64))
#     email = db.Column(db.String(64), index=True)
#     subject = db.Column(db.String(128))
#     body_text = db.Column(db.Text())
#     body_html = db.Column(db.Text())
#     #talk_id = db.Column(db.Integer, db.ForeignKey('talks.id'))
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

#     # @staticmethod
#     # def already_in_queue(email, talk):
#     #     return PendingEmail.query\
#     #         .filter(PendingEmail.talk_id == talk.id)\
#     #         .filter(PendingEmail.email == email).count() > 0

#     @staticmethod
#     def remove(email):
#         PendingEmail.query.filter_by(email=email).delete()


