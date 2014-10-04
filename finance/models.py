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

    def str_to_date(self, date_launch):
        date = date_launch.replace('/','-')
        return datetime.strptime(date, '%d-%m-%Y').date()

    def get_date_purchase(self, date, launch):
        if launch.strip()[-3] == '/':
            date_purchase = launch.strip()[-5:].replace('/','-')
            date = date_purchase + '-' + str(date.year)
            date = datetime.strptime(date, '%d-%m-%Y').date()
        return date

    def str_to_float(self, value):
        value = float(value.replace(',','.'))
        return float("{0:.2f}".format(round(value,2)))

    def is_equal(self, date_launch, launch, value):
        if value < 0:
            t = Extract.objects.filter(date_launch=date_launch, launch=launch.strip(), value_debit=abs(value)) 
        else:
            t = Extract.objects.filter(date_launch=date_launch, launch=launch.strip(), value_credit=value) 

        return t

    def importer(self, path='/Users/neto/Dropbox/projetcs/balance-pack/extrato.txt'):
        with open(path, 'r') as ff:
            contents = ff.readlines()
            line = 0
            while line < len(contents):
                extract = Extract()
                date_launch, launch, value = contents[line].split(';')
                date_launch = extract.str_to_date(date_launch)
                launch = launch.strip()   #.split('-')[:-1]
                value = extract.str_to_float(value)
                
                #import pdb; pdb.set_trace()
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

                line += 1

            ff.close()