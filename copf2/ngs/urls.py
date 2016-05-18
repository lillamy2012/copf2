from django.conf.urls import url

from . import views

urlpatterns = [
               url(r'^$', views.index, name='index'),
               url(r'^scientists', views.scientists, name='scientists'),
                url(r'^samples', views.samples, name='samples'),
                url(r'^flowlanes', views.flowlanes, name='flowlanes'),
               ]
