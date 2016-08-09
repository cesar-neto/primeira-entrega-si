#!-*- conding: utf8 -*-
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from .models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.core.files.base import ContentFile



def index(request):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        return redirect('/app')
    except:
        return render_to_response('login.html', {}, context_instance=RequestContext(request))
        
# Falta criar o template register.html
# Falta exportar base.html
def registro(request):
    if request.method == 'GET':
        return render_to_response('registro.html', {}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        nome = request.POST['nome']
        email = request.POST['email']
        senha = request.POST['senha']

        try:
            us_temp = Usuario.objects.get(email=email)
            messages.error(request, 'Email ja cadastrado')

            return render_to_response('registro.html', {}, context_instance=RequestContext(request))


        except:
            new_usuario = Usuario(nome=nome, email=email, senha=senha)
            new_usuario.save()
            messages.success(request, 'Usuario criado com sucesso')
            return redirect('/')


def login(request):
    if request.method == 'GET':
       return redirect('/')
    elif request.method == 'POST':
        email = request.POST['email']
        senha = request.POST['senha']
        try:
            usuario = Usuario.objects.get(email=email)
            if senha == usuario.senha:
                request.session['email'] = usuario.email
                return redirect('/app')
            else:
                messages.error(request, 'Senha Incorreta')
            return redirect('/')
            # return render_to_response('login.html', {}, context_instance=RequestContext(request))
        except:
            messages.error(request, 'Usuario nao cadastrado')
            return redirect('/')
            # return render_to_response('login.html', {}, context_instance=RequestContext(request))
    

def app(request):
    usuario = Usuario.objects.get(email=request.session['email'])
    return render_to_response('app.html', {'usuario': usuario}, context_instance=RequestContext(request))


def view_pasta(request, id):
    usuario = Usuario.objects.get(email=request.session['email'])
    pasta = Pasta.objects.get(id=id)
    return render_to_response('view_pasta.html', {'pasta': pasta}, context_instance=RequestContext(request))


def create_arquivo(request):
    usuario = Usuario.objects.get(email=request.session['email'])
    if request.method == 'GET':
        return render_to_response('create_file.html', {'usuario': usuario}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        nome = request.POST['nome']
        tipo = request.POST['tipo']
        if 'pasta' in request.POST:
            pasta = Pasta.objects.get(id=request.POST['pasta'])
        else:
            pasta = None
        try:
            file = ContentFile(request.POST['content'])
            arquivo = Arquivo(nome=nome, tipo=tipo, pasta=pasta)
            arquivo.arquivo.save(nome+'.'+tipo, file)
            arquivo.save()
            usuario.arquivos.add(arquivo)
            usuario.save()
            messages.success(request, 'Arquivo adicionado com sucesso')
            if pasta:
                return redirect('/pasta/'+str(pasta.id))
            else:
                return redirect('/')
        except:
            messages.error(request, 'Nao foi possivel criar novo arquivo')
            return render_to_response('create_file.html', {'usuario': usuario}, context_instance=RequestContext(request)) 
        
        
def edit_arquivo(request, id):
    arquivo = Arquivo.objects.get(id=id)
    if request.method == 'GET':
        file = arquivo.arquivo
        file.open(mode='rb') 
        content = file.readlines()
        file.close()
        return render_to_response('view_file.html', {'arquivo':arquivo, 'content': content}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        myfile = ContentFile(request.POST['content'])
        arquivo.arquivo.save(str(arquivo.nome)+'.'+arquivo.tipo, myfile)
        arquivo.save()
        myfile.open(mode='rb') 
        content = myfile.readlines()
        myfile.close()
        messages.success(request, 'Alterado com sucesso')
        return render_to_response('view_file.html', {'arquivo':arquivo, 'content': content}, context_instance=RequestContext(request))
        

def nova_pasta(request):
    if request.method == 'GET':
        usuario = Usuario.objects.get(email=request.session['email'])
        return render_to_response('nova_pasta.html', {'usuario':usuario}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        titulo = request.POST['titulo']
        descricao = request.POST['descricao']
        if 'pasta' in request.POST:
            past = Pasta.objects.get(id=request.POST['pasta'])
        else:
            past = None
        try:
            pasta = Pasta(titulo=titulo, desc=descricao)
            pasta.save()
            usuario = Usuario.objects.get(email=request.session['email'])
            usuario.pastas.add(pasta)
            usuario.save()
            messages.success(request, 'Pasta criada com sucesso')
            return redirect('/app')
        except:
            messages.error(request, 'Nao foi possivel criar a pasta')
            return render_to_response('nova_pasta.html', {}, context_instance=RequestContext(request))


def logout(request):
    request.session.clear()
    return redirect('/')
