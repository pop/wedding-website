from django.core.management import BaseCommand
from guests import csv_import
from sys import stderr


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='File to import from.')
        parser.add_argument('--url', type=str, help='URL to import from.')

    def handle(self, *args, **kwargs):
        if kwargs.get('file'):
            print("importing FILE {}.".format(kwargs['file']))
            csv_import.import_guests(kwargs['file'])
        elif kwargs.get('url'):
            print("importing URL {}.".format(kwargs['url']))
            csv_import.import_guests_url(kwargs['url'])
        else:
            print("Please provde a URL or FILE.")
            exit(1)
