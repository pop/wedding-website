from email.mime.image import MIMEImage
import os
from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.http import Http404
from django.template.loader import render_to_string
from guests.models import Party

INVITATION_TEMPLATE = 'guests/email_templates/invitation.html'


def guess_party_by_invite_id_or_404(invite_id):
    try:
        return Party.objects.get(invitation_id=invite_id)
    except Party.DoesNotExist:
        if settings.DEBUG:
            # in debug mode allow access by ID
            return Party.objects.get(id=int(invite_id))
        else:
            raise Http404()


def get_invitation_context(party):
    return {
        'page_title': "Lucy & Eli - you're invited!",
        'main_image': "table-top.jpg",
        'invitation_id': party.invitation_id,
        'party': party,
        'guests': ' & '.join([m.first_name for m in party.guest_set.all()])
    }


def send_invitation_email(party, test_only=False, recipients=None):
    if recipients is None:
        recipients = party.guest_emails
    if not recipients:
        print ('===== WARNING: no valid email addresses found for {} ====='.format(party))
        return

    context = get_invitation_context(party)
    context['email_mode'] = True
    context['site_url'] = settings.WEDDING_WEBSITE_URL
    template_html = render_to_string(INVITATION_TEMPLATE, context=context)
    template_text = "You're invited to {}'s wedding! View your invitation at {}".format(
        settings.BRIDE_AND_GROOM,
        reverse('invitation', args=[context['invitation_id']])
    )
    subject = "Eli & Lucy Are Getting Married!"
    # https://www.vlent.nl/weblog/2014/01/15/sending-emails-with-embedded-images-in-django/
    msg = EmailMultiAlternatives(subject, template_text, settings.DEFAULT_WEDDING_FROM_EMAIL, recipients,
                                 reply_to=[settings.DEFAULT_WEDDING_REPLY_EMAIL])
    msg.attach_alternative(template_html, "text/html")
    msg.mixed_subtype = 'related'
    for filename in (context['main_image'], ):
        attachment_path = os.path.join(os.path.dirname(__file__), 'static', 'invitation', 'images', filename)
        with open(attachment_path, "rb") as image_file:
            msg_img = MIMEImage(image_file.read())
            msg_img.add_header('Content-ID', '<{}>'.format(filename))
            msg.attach(msg_img)

    print ('sending invitation to {} ({})'.format(party.name, ', '.join(recipients)))
    if not test_only:
        msg.send()


def send_all_invitations(test_only, mark_as_sent):
    to_send_to = Party.objects.filter(is_invited=True, invitation_sent=None).exclude(is_attending=False)
    for party in to_send_to:
        send_invitation_email(party, test_only=test_only)
        if mark_as_sent:
            party.invitation_sent = datetime.now()
            party.save()
