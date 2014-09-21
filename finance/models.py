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

    def importer(self, path):
        with open(path, 'rb') as ff:
            import pdb; pdb.set_trace()
            contents = ff.read()
            line = 0
            while line <= len(contents):
                date_launch, launch_aux, value_debit = contents[line].split(';')
                extract.launch = launch_aux.strip()[:-6]
                extract.date_purchase = launch_aux.strip()[-5:]
                extract.save()
                line += 1

            ff.close()
