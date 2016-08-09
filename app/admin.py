from django.contrib import admin
from django import forms

from .models import *

admin.site.register(Arquivo)
admin.site.register(Usuario)
admin.site.register(Pasta)
