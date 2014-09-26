from django.db import models
from datetime import *


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

    def importer(self, path):
        with open(path, 'r') as ff:
            import pdb; pdb.set_trace()
            contents = ff.readlines()
            line = 0
            extract = Extract()
            while line <= len(contents):
                extract.date_launch, launch_aux, extract.value_debit = contents[line].split(';')
                if launch_aux[-3] == '/':
                    extract.launch = launch_aux.strip('-')[0].strip()
                    extract.date_purchase = launch_aux.split('-')[1]
                else:
                    extract.launch = launch_aux.strip()
                extract.save()
                line += 1

            ff.close()