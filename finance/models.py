from django.db import models


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

	# type_id_launch = models.ManyToManyField(TypeLaunch, blank=True, null=True, 
	# 										help_text='Please select one Type Id launch for each extract requested.')