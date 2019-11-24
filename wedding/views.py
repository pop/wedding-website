from django.conf import settings
from django.shortcuts import render


def home(request):
    return render(request, 'home.html', context={
        'support_email': settings.DEFAULT_WEDDING_REPLY_EMAIL,
    })
