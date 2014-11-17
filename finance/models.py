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

	def report_week(self, date=''):
		extract = Extract()
		extract.importer()
		date = datetime.today().date()
		#date = datetime.strptime('25-10-2014', '%d-%m-%Y').date()
		fri = 4
		n = 0
		week = date.weekday()
		first_day_week = self.dif_date(date, week)
		#import ipdb; ipdb.set_trace()
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


