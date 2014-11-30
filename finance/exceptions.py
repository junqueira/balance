# -*- coding: utf-8 -*-

"""
finance.exceptions
~~~~~~~~~~~~~~~~~~
Exceptions used in finance module.
"""
class FinanceException(Exception):
		"""A base class for gspread's exceptions."""

class IncorrectCellLabel(FinanceException):
		"""The cell label is incorrect."""