#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
	from django.core.management import execute_from_command_line
	#execute_from_command_line(sys.argv)

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from finance import create_app
from flask.ext.script import Manager
from finance import db
from finance.models import User

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


@manager.command
def test():
    from subprocess import call
    call(['nosetests', '-v',
          '--with-coverage', '--cover-package=app', '--cover-branches',
          '--cover-erase', '--cover-html', '--cover-html-dir=cover'])


#python3 manage.py adduser --admin lcjneto@gmail.com luiz
@manager.command
def adduser(email, username, admin=False):
    """Register a new user."""
    from getpass import getpass
    password = getpass()
    password2 = getpass(prompt='Confirm: ')
    if password != password2:
        import sys
        sys.exit('Error: passwords do not match.')
    db.create_all()
    user = User(email=email, username=username, password=password, is_admin=admin)
    db.session.add(user)
    db.session.commit()
    print('User {0} was registered successfully.'.format(username))


if __name__ == '__main__':
    manager.run()

