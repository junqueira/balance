from django.db import models
from datetime import datetime
from django.contrib.contenttypes.models import *


class TypeLaunch(models.Model):
    type_name = models.CharField(max_length=100, unique=True)


class Provider(models.Model):
    description = models.CharField(max_length=100, unique=True)
    type_launch = models.ForeignKey(TypeLaunch, blank=True, null=True)
    date_last_purchase = models.DateField('date last purchase')
    value_total = models.DecimalField(max_digits=8, decimal_places=2)


class Extract(models.Model):
    date_launch = models.DateField('date launch')
    launch = models.CharField(max_length=100)
    date_purchase = models.DateField('date purchase')
    value_debit = models.DecimalField(max_digits=8, decimal_places=2)
    value_credit = models.DecimalField(max_digits=8, decimal_places=2)
    value_balance = models.DecimalField(max_digits=8, decimal_places=2)
    cancelled = models.BooleanField(default=True, db_index=True)
    provider = models.ForeignKey(Provider, blank=True, null=True)

    def str_to_date(self, date_launch, launch=''):
        date = date_launch.replace('/','-')
        if not launch is '' and launch.strip()[-3] == '/':
            year = datetime.strptime(date, '%d-%m-%Y').date().year 
            date = launch.strip()[-5:].replace('/','-') + '-' + str(year)

        return datetime.strptime(date, '%d-%m-%Y').date()

    def str_to_float(self, value):
        value = float(value.replace(',','.'))
        return float("{0:.2f}".format(round(value,2)))

    def importer(self, path='/Users/neto/Dropbox/projetcs/balance-pack/extrato.txt'):
        with open(path, 'r') as ff:
            contents = ff.readlines()
            line = 0
            while line < len(contents):
                #import pdb; pdb.set_trace()
                date_launch, launch, value = contents[line].split(';')

                extract = Extract()
                extract.date_launch = extract.str_to_date(date_launch)
                extract.launch = launch.strip()   #.split('-')[:-1]
                extract.date_purchase = extract.str_to_date(date_launch, launch)
                
                if extract.str_to_float(value) < 0:
                    extract.value_debit = abs(extract.str_to_float(value))
                    extract.value_credit = 0
                else:
                    extract.value_debit = 0
                    extract.value_credit = extract.str_to_float(value)

                extract.value_balance = 0
                
                extract.save()
                line += 1

            ff.close()