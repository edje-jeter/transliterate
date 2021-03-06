from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^input_output/$', 'main.views.input_output'),
    url(r'^arpabet_entry/$', 'main.views.arpabet_entry', name='arpabet_entry'),
    url(r'^name_func/$', 'main.views.name_func', name='name_func'),
    url(r'^name_batch_process/$', 'main.views.name_batch_process', name='name_batch_process'),
    url(r'^continuous_process/$', 'main.views.continuous_process', name='continuous_process'),
    url(r'^batch_process/$', 'main.views.batch_process', name='batch_process'),
    url(r'^add_word_to_dict/$', 'main.views.add_word_to_dict', name='add_word_to_dict'),
    url(r'^generate_keyboard/$', 'main.views.generate_keyboard', name='generate_keyboard'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
