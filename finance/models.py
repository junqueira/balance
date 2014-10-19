from django.db import models
from datetime import datetime
from django.contrib.contenttypes.models import *
from finance.worksheet import *


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

    def dif_date(self, date, day):
        return date.fromordinal(date.toordinal()-day)

    def print_launch(self, date):
        extract = Extract.objects.filter(date_purchase=date)
        cust_day = 0
        cust_total = 0
        for x in extract:
            cust_day += x.value_debit
            cust_total += cust_day
            print(' # ' + str(x.launch) + ' => ' + str(x.value_debit))
        print(' ## ' + str(cust_day) + ' ## ')

    def report_week(self, date=''):
        #date = datetime.strptime('09-05-2014', '%d-%m-%Y').date()
        extract = Extract()
        extract.importer()

        date = datetime.today().date()
        numWeek = date.isocalendar()
        DayL = ['Mon', 'Tues', 'Wednes', 'Thurs', 'Fri', 'Satur', 'Sun']
        # the weekly cost and so closed 'Fri', 'Satur' or 'Sun'
        fri = 4
        n = 0
        week = date.weekday()
        while n < len(DayL):
            if week < fri:
                day = self.dif_date(date, 7 + week - n)
            else:
                day = self.dif_date(date, week - n)
            print(str(day) + ' => ' + DayL[n] + 'day')
            self.print_launch(day)
            n += 1

        w = WorkSheet()
        w.send()

    def provider_type(self, launch):
        prov = Provider.objects.filter(description=launch)
        if prov.exists() and prov[0].type_launch_id is None:
            print('Provider => ' + launch + ' does not exist cost')

    def str_to_date(self, date_launch):
        date = date_launch.replace('/','-')
        return datetime.strptime(date, '%d-%m-%Y').date()

    def get_date_purchase(self, date, launch):
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

    def importer(self, path='/Users/neto/Downloads/extrato.txt'):
        with open(path, 'r') as ff:
            contents = ff.readlines()
            line = 0
            while line < len(contents):
                extract = Extract()
                date_launch, launch, value = contents[line].split(';')
                date_launch = extract.str_to_date(date_launch)
                launch = extract.get_launch(launch)
                value = extract.str_to_float(value)

                if not extract.is_equal(date_launch, launch, value).exists():
                    extract.date_launch = date_launch
                    extract.launch = launch
                    extract.date_purchase = extract.get_date_purchase(date_launch, launch)

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