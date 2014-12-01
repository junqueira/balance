#!/usr/bin/env python
import argparse
import json
import os
import requests

from colorama import init, Fore
           #
API_KEY = '9cebbbee11ec863600da7fdabed04caf'
API_URL = 'https://api.trello.com/1/'
APP_NAME = 'trello-cmd'
CONFIG = os.path.join(os.environ['HOME'], '.trello')

class NoConfigException(Exception):
    pass

class TrelloClient:

    def __init__(self):
        self._config = {}
        self._boards = {}
        self._orgs = {}

    def read_config(self):
        if os.path.isfile(CONFIG):
            config_file = open(CONFIG, 'r')
            self._config = json.loads(config_file.read())
        else:
            raise NoConfigException('Configuration file does not exists.')

    def list_boards(self, org=None):
        if not org:
            url = 'members/my/boards?filter=open&key=%s&token=%s' % (API_KEY,
                self._config['token'])
        else:
            url = 'organization/%s/boards?filter=open&key=%s&token=%s' % (org,
                API_KEY, self._config['token'])

        r = requests.get('%s%s' % (API_URL, url))
        # print Fore.GREEN + 'Boards' + Fore.RESET
        for board in r.json():
            # print('  ' + board['name'] + ' (') + \
                self.get_org(board['idOrganization'])['displayName'] + ')'

    def list_orgs(self, should_print=True):
        self._orgs = {}

        r = requests.get('%smembers/my/organizations?key=%s&token=%s' % (
            API_URL, API_KEY, self._config['token']))

        # if should_print:
            # print Fore.GREEN + 'Organizations' + Fore.RESET
            # print '  %-15s %s' % ('Board Name', 'Board Display Name')
            # print '  %-15s %s' % ('----------', '------------------')

        for org in r.json():
            self._orgs[org['id']] = {
                'name': org['name'],
                'displayName': org['displayName']
            }
            # if should_print:
            #     print '  %-15s %s' % (org['name'], org['displayName'])

        return self._orgs

    def get_org(self, org_id=None):
        try:
            return self._orgs[org_id]
        except KeyError:
            r = requests.get('%sorganizations/%s?key=%s&token=%s' % (API_URL,
                org_id, API_KEY, self._config['token']))
            org = r.json()
            self._orgs[org['id']] = {
                'name': org['name'],
                'displayName': org['displayName']
            }
            return self._orgs[org['id']]

    def setup(self):
        """Set up the client for configuration"""
        if os.path.isfile(CONFIG):
            os.remove(CONFIG)

        auth_url = '%sauthorize?key=%s&name=%s&expiration=never&response_type='\
                'token&scope=read,write' % (API_URL, API_KEY, APP_NAME)
        # print 'Open %s in your web browser' % auth_url
        token = raw_input('Paste the token: ')

        config_file = open(CONFIG, 'w')
        config_file.write(json.dumps({'token': token}))
        config_file.close()

        # print Fore.GREEN + 'Your config is ready to go!' + Fore.RESET

    def run(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(help='commands')
        board_parser = subparsers.add_parser('boards', help='Board operations')
        board_parser.add_argument('-o', '--org', action='store', help='''List
            boards for specific organizations''')
        board_parser.set_defaults(which='board')

        org_parser = subparsers.add_parser('orgs', help='List organizations')
        org_parser.set_defaults(which='org')

        config_parser = subparsers.add_parser('reconfig',
                help='Reconfigure the client')
        config_parser.set_defaults(which='reconfig')

        options = parser.parse_args()

        if not os.path.isfile(CONFIG) or options.which is 'reconfig':
            self.setup()
        elif options.which is 'board':
            self.read_config()
            self.list_boards()
        elif options.which is 'org':
            self.read_config()
            self.list_orgs()


if __name__ == '__main__':
    init() # Initialize colorama
    client = TrelloClient()
    client.run()