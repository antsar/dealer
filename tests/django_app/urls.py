from django.conf.urls import url
from django.http import HttpResponse


urlpatterns = [
    url(r'^revision/', lambda r: HttpResponse(r.revision)),
    url(r'^tag/', lambda r: HttpResponse(r.tag)),
    url(r'^revision_date/', lambda r: HttpResponse(r.revision_date)),
]
