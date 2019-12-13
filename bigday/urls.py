from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from django.http import HttpResponse


def certbot(request):
    return HttpResponse('Jd-bya_yMeAy5cE8zVy5_yItpTnutOfy_NzikS5d06I.BPKCFV9KrBdiyfvEmhNEs-hc-MsSf9giX1tmV5-fU28')


urlpatterns = [
    url(r'^', include('wedding.urls')),
    url(r'^', include('guests.urls')),
    url(r'^admin/', admin.site.urls),
    url('^accounts/', include('django.contrib.auth.urls')),
    path('.well-known/acme-challenge/Jd-bya_yMeAy5cE8zVy5_yItpTnutOfy_NzikS5d06I', certbot)
]
