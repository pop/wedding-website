import csv
import io
import uuid

from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from guests.models import Party, Guest
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

WRITE_CHUNK_SIZE = 16 * 1024

def import_guests_url(url):
    """
    Fetch contents from a URL and pass it through to `import_guests`
    """
    with NamedTemporaryFile() as f:
        # Get the contents of the given URL
        response = urlopen(url)
        # Read the first chunk from the response
        chunk = response.read(WRITE_CHUNK_SIZE)
        # Continue to read chunks until we're all out of chunks
        while chunk:
            f.write(chunk)
            chunk = response.read(WRITE_CHUNK_SIZE)
        # Seek to the beginning of the file so import_guests can read it
        f.seek(0)
        # Return the file name to read from in import_guests
        return import_guests(f.name)

def import_guests(path):
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        first_row = True
        for row in reader:
            if first_row:
                first_row = False
                continue
            party_name, first_name, last_name, email = row[:8]
            if not party_name:
                print ('skipping row {}'.format(row))
                continue
            party = Party.objects.get_or_create(name=party_name)[0]
            party.is_invited = True
            if not party.invitation_id:
                party.invitation_id = uuid.uuid4().hex
            party.save()
            if email:
                guest, created = Guest.objects.get_or_create(party=party, email=email)
                guest.first_name = first_name
                guest.last_name = last_name
            else:
                guest = Guest.objects.get_or_create(party=party, first_name=first_name, last_name=last_name)[0]
            guest.save()


def export_guests():
    headers = [
        'party_name', 'first_name', 'last_name', 'is_invited', 'is_attending',
        'rehearsal_dinner', 'email', 'comments'
    ]
    file = io.StringIO()
    writer = csv.writer(file)
    writer.writerow(headers)
    for party in Party.in_default_order():
        for guest in party.guest_set.all():
            if guest.is_attending:
                writer.writerow([
                    party.name,
                    guest.first_name,
                    guest.last_name,
                    party.is_invited,
                    guest.is_attending,
                    party.rehearsal_dinner,
                    guest.email,
                    party.comments,
                ])
    return file


def _is_true(value):
    value = value or ''
    return value.lower() in ('y', 'yes')
