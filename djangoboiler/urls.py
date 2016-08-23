"""djangoboiler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin/login/$', auth_views.login),
    url(r'^$', views.index, name='index'),
    url(r'^login', views.login, name='login'),
    url(r'^registro', views.registro, name='register'),
    url(r'^app', views.app, name='app'),
    url(r'^logout', views.logout, name='logout'),
    url(r'^pasta/(?P<id>[0-9]+)', views.view_pasta, name='viewpasta'),
    url(r'^edit-arquivo/(?P<id>[0-9]+)', views.edit_arquivo, name='editarquivo'),
    url(r'^nova-pasta', views.nova_pasta, name='novapasta'),
    url(r'^novo-arquivo', views.create_arquivo, name='novoarquivo'),
    url(r'^lixeira', views.lixeira, name='lixeira'),
    url(r'^remove-arquivo/(?P<id>[0-9]+)', views.remove_arquivo, name='removearquivo'),
    url(r'^remove-pasta/(?P<id>[0-9]+)', views.remove_pasta, name='removepasta'),
    url(r'^upload-arquivo', views.upload_arquivo, name='uploadarquivo'),
    url(r'^share-arquivo/(?P<id>[0-9]+)', views.share_arquivo, name='sharearquivo'),
    url(r'^arquivo/(?P<id>[0-9]+)', views.view_file, name='viewfile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
