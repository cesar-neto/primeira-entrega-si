from __future__ import unicode_literals

from django.db import models

TIPOS = (

    ('txt', 'md'),
)

class Pasta(models.Model):
    titulo = models.CharField(max_length=100)
    desc = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    editado_em = models.DateTimeField(auto_now=True)
    

class Arquivo(models.Model):
    nome = models.CharField(max_length=100)
    arquivo = models.FileField()
    pasta = models.ForeignKey(Pasta, blank=True, null=True)
    tipo = models.CharField(max_length=50, choices=TIPOS)
    status = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    editado_em = models.DateTimeField(auto_now=True)
    

class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    senha = models.CharField(max_length=20)
    pastas = models.ManyToManyField(Pasta, blank=True)
    arquivos = models.ManyToManyField(Arquivo, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    editado_em = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'%s' % (self.email)
        
    
    
    
