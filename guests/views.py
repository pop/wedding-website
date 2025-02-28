import base64
from collections import namedtuple
import random
from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView
from guests import csv_import
from guests.invitation import get_invitation_context, INVITATION_TEMPLATE, guess_party_by_invite_id_or_404, \
    send_invitation_email
from guests.models import Guest, Party

class GuestListView(ListView):
    model = Guest


@login_required
def export_guests(request):
    export = csv_import.export_guests()
    response = HttpResponse(export.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=all-guests.csv'
    return response


@login_required
def dashboard(request):
    parties_with_pending_invites = Party.objects.filter(
        is_invited=True, is_attending=None
    )
    parties_with_unopen_invites = parties_with_pending_invites.filter(invitation_opened=None)
    parties_with_open_unresponded_invites = parties_with_pending_invites.exclude(invitation_opened=None)
    attending_guests = Guest.objects.filter(is_attending=True)
    return render(request, 'guests/dashboard.html', context={
        'guests': Guest.objects.filter(is_attending=True).count(),
        'possible_guests': Guest.objects.filter(party__is_invited=True).exclude(is_attending=False).count(),
        'not_coming_guests': Guest.objects.filter(is_attending=False).count(),
        'pending_invites': parties_with_pending_invites.count(),
        'pending_guests': Guest.objects.filter(party__is_invited=True, is_attending=None).count(),
        'parties_with_unopen_invites': parties_with_unopen_invites,
        'parties_with_open_unresponded_invites': parties_with_open_unresponded_invites,
        'unopened_invite_count': parties_with_unopen_invites.count(),
        'total_invites': Party.objects.filter(is_invited=True).count(),
    })


def invitation(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    if party.invitation_opened is None:
        # update if this is the first time the invitation was opened
        party.invitation_opened = datetime.utcnow()
        party.save()
    if request.method == 'POST':
        for response in _parse_invite_params(request.POST):
            guest = Guest.objects.get(pk=response.guest_pk)
            assert guest.party == party
            guest.is_attending = response.is_attending
            guest.save()
        if request.POST.get('comments'):
            comments = request.POST.get('comments')
            party.comments = comments if not party.comments else '{}; {}'.format(party.comments, comments)
        party.is_attending = party.any_guests_attending
        party.save()
        return HttpResponseRedirect(reverse('rsvp-confirm', args=[invite_id]))
    return render(request, template_name='guests/invitation.html', context={
        'party': party,
    })


InviteResponse = namedtuple('InviteResponse', ['guest_pk', 'is_attending'])


def _parse_invite_params(params):
    responses = {}
    for param, value in params.items():
            pk = int(param.split('-')[-1])
            response = responses.get(pk, {})
            response['attending'] = True if value == 'yes' else False
            responses[pk] = response
    for pk, response in responses.items():
        yield InviteResponse(pk, response['attending'])


def rsvp_confirm(request, invite_id=None):
    party = guess_party_by_invite_id_or_404(invite_id)
    return render(request, template_name='guests/rsvp_confirmation.html', context={
        'party': party,
        'support_email': settings.DEFAULT_WEDDING_REPLY_EMAIL,
    })


@login_required
def invitation_email_preview(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    context = get_invitation_context(party)
    return render(request, INVITATION_TEMPLATE, context=context)


@login_required
def invitation_email_test(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    send_invitation_email(party, recipients=[settings.DEFAULT_WEDDING_TEST_EMAIL])
    return HttpResponse('sent!')

def _base64_encode(filepath):
    with open(filepath, "rb") as image_file:
        return base64.b64encode(image_file.read())
