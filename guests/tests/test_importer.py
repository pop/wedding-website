import os
from django.test import TestCase
from guests.csv_import import import_guests
from guests.models import Party, Guest


class GuestImporterTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(GuestImporterTest, cls).setUpClass()
        cls.path = os.path.join(os.path.dirname(__file__), 'data', 'guests-test.csv')
        import_guests(cls.path)

    def test_import(self):
        self.assertEqual(3, Party.objects.count())
        self.assertEqual(5, Guest.objects.count())
        the_starks = Guest.objects.filter(party__name='The Starks')
        self.assertEqual(3, the_starks.count())

    def test_import_idempotent(self):
        for i in range(3):
            import_guests(self.path)
            self.assertEqual(3, Party.objects.count())
            self.assertEqual(5, Guest.objects.count())
            the_starks = Guest.objects.filter(party__name='The Starks')
            self.assertEqual(3, the_starks.count())

    def test_is_invited(self):
        for party in Party.objects.all():
            self.assertTrue(party.is_invited)

    def test_email(self):
        self.assertEqual('ned@winterfell.gov', Guest.objects.get(first_name='Ned').email)

    def test_email_default(self):
        self.assertEqual(None, Guest.objects.get(first_name='Tyrion').email)

