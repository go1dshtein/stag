#!/usr/bin/env python3
import argparse
import datetime
import httplib2
import json
import os
import re
import shutil
import urllib.parse
import locale

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


SHEET_ID = 'sheet_id'
APPLICATION_NAME = 'Stag'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'


def parse_args(args=None):
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    subparsers = parser.add_subparsers(
        title='subcommands', dest='subcommand')

    setup = subparsers.add_parser(
        'setup', help='setup the program')
    setup.add_argument(
        'sheet', help='link to your google sheet')
    setup.add_argument(
        'secret', help=(
            'filename with secret api token, '
            'you can get it here '
            'https://console.developers.google.com'
            '/start/api?id=sheets.googleapis.com'))

    start = subparsers.add_parser(
        'start', help='write the start time')

    stop = subparsers.add_parser(
        'stop', help='write the stop time')

    return parser.parse_args(args)


def get_config_filename(name=None):
    if name is None:
        name = 'config'
    filename = os.path.realpath(
        os.path.join(os.path.expanduser('~'), '.stag', '%s.json' % name))
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        os.chmod(dirname, 0o700)
    return filename


def read_config():
    filename = get_config_filename()
    try:
        with open(filename) as h:
            return json.loads(h.read())
    except OSError:
        return {}


def write_config(config):
    filename = get_config_filename()
    with open(filename, 'w') as h:
        h.write(json.dumps(config, indent=2))
    os.chmod(filename, 0o600)


def save_secret(secret):
    filename = get_config_filename('secret')
    shutil.copy(secret, filename)
    os.chmod(filename, 0o600)


def get_credentials(args, force=False):
    secret = get_config_filename('secret')
    filename = get_config_filename('credentials')
    store = Storage(filename)
    credentials = store.get()
    if force or not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(secret, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, args)
    return credentials


def get_service(args):
    credentials = get_credentials(args)
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = (
        'https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    return service


def get_sheet_name(service, sheet_id, timestamp):
    timestamp = timestamp.strftime('%B %Y')
    sheets = service.spreadsheets().get(
        spreadsheetId=sheet_id).execute()
    sheets = sheets.get('sheets', [])
    sheets = [x.get('properties', {}).get('title', '') for x in sheets]
    sheets = [x for x in sheets if x.find(timestamp) >= 0]
    if not sheets:
        raise RuntimeError('could no find sheet for date %s' % timestamp)
    if len(sheets) > 1:
        raise RuntimeError('too many sheets found: %s' % sheets)
    return sheets[0]


def get_cell(service, sheet_id, timestamp, kind):
    START_ROW = 7
    NUMBER_OF_ROWS = 1 + 31

    if kind == 'start':
        col = 'C'
    elif kind == 'stop':
        col = 'D'
    else:
        raise RuntimeError('unknown operation kind: %s' % kind)

    sheet_name = get_sheet_name(service, sheet_id, timestamp)
    timestamp = timestamp.strftime('%d.%m.%Y')

    rangeName = '%s!A%d:A%d' % (
        sheet_name, START_ROW, START_ROW + NUMBER_OF_ROWS)

    values = service.spreadsheets().values().get(
        spreadsheetId=sheet_id, range=rangeName).execute()
    values = values.get('values', [])
    for i, row in enumerate(values, START_ROW):
        address = '%s!%s%d' % (sheet_name, col, i)
        if row and row[0].find(timestamp) >= 0:
            return address

    raise RuntimeError('could not find row with date %s' % timestamp)


def set_value(service, sheet_id, cell, value):
    body = {
        'range': cell,
        'majorDimension': 'ROWS',
        'values': [
            [value]
        ]
    }

    result = service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=cell,
        body=body, valueInputOption='USER_ENTERED').execute()
    print(result)


def setup_cmd(args):
    path = urllib.parse.urlparse(args.sheet).path
    found = re.search('/spreadsheets/d/(\w+)(/edit|/)?$', path, re.S | re.M)
    if not found:
        raise RuntimeError('seems sheet\'s link is invalid')
    write_config({SHEET_ID: found.group(1)})
    save_secret(args.secret)
    credentials = get_credentials(args, force=True)


def update_cmd(args):
    timestamp = datetime.datetime.now()
    sheet_id = read_config().get(SHEET_ID)
    if not sheet_id:
        raise RuntimeError('please setup program before')

    service = get_service(args)
    cell = get_cell(service, sheet_id, timestamp, args.subcommand)
    set_value(service, sheet_id, cell, timestamp.strftime('%H:%M'))


def main(args):
    locale.setlocale(locale.LC_ALL, 'C')
    if args.subcommand == 'setup':
        setup_cmd(args)
    elif args.subcommand in ('start', 'stop'):
        update_cmd(args)

if __name__ == '__main__':
    main(parse_args())
