from django.db import models
from datetime import datetime


class TypeLaunch(models.Model):
    type_name = models.CharField(max_length=100, unique=True)


class Provider(models.Model):
    description = models.CharField(max_length=100, unique=True)
    type_launch = models.ForeignKey(TypeLaunch, blank=True, null=True)
    date_last_purchase = models.DateTimeField('date last purchase')
    value_total = models.DecimalField(max_digits=5, decimal_places=2)


class Extract(models.Model):
    date_launch = models.DateTimeField('date launch')
    launch = models.CharField(max_length=100)
    date_purchase = models.DateTimeField('date purchase')
    value_debit = models.DecimalField(max_digits=5, decimal_places=2)
    value_credit = models.DecimalField(max_digits=5, decimal_places=2)
    value_balance = models.DecimalField(max_digits=5, decimal_places=2)
    cancelled = models.BooleanField(default=True, db_index=True)
    provider = models.ForeignKey(Provider, blank=True, null=True)

    def str_to_date(self, date_launch, launch, year):
        #import pdb; pdb.set_trace()
        if launch.strip()[-3] == '/':
            date = launch.split('-')[-1].strip()
            date = date.replace('/','-') + '-' + str(year)

        return datetime.strptime(date, '%d-%m-%Y').date()

    def str_to_float(self, value):
        return float(value.replace(',','.'))

    def importer(self, path):
        with open(path, 'r') as ff:
            contents = ff.readlines()
            line = 0
            extract = Extract()
            while line <= len(contents):
                date_launch, launch, value = contents[line].split(';')
                extract.date_launch = datetime.strptime(date_launch, '%d-%m-%Y').date()
                extract.launch = launch.strip()   #.split('-')[:-1]
                year = extract.str_to_date(date_launch).year
                extract.date_purchase = extract.str_to_date(date_launch, launch, year)

                if extract.str_to_float(value) < 0:
                    extract.value_debit = extract.str_to_float(value)
                    extract.value_credit = 0
                else:
                    extract.value_debit = 0
                    extract.value_credit = extract.str_to_float(value)

                extract.value_balance = 0
                extract.save()
                line += 1

            ff.close()