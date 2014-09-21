from django.db import models
import os

class Import(models.Model):

	def extract_import(self, **kwargs):
		while not os.path.isfile()