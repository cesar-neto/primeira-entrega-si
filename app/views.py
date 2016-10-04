#!-*- conding: utf8 -*-
# coding=utf-8
from __future__ import print_function
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from .models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.core.files.base import ContentFile
import re


def index(request):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        return redirect('/app')
    except:
        return render_to_response('login.html', {}, context_instance=RequestContext(request))

# Função usada no registro do usuario, utilizando nome, email, senha e sua confirmação
# Não é permitido usuarios com mesmo nome ou email
def registro(request):
    if request.method == 'GET':
        return render_to_response('registro.html', {}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        nome = request.POST['nome']
        email = request.POST['email']
        senha = request.POST['senha']
        confirmacao_senha = request.POST['confirmacao_senha']

        try:
            if senha != confirmacao_senha:
                messages.error(request, 'Senhas nao coincidem')
                return render_to_response('registro.html', {}, context_instance=RequestContext(request))

            elif Usuario.objects.get(email=email):
                messages.error(request, 'Email ja cadastrado')
                return render_to_response('registro.html', {}, context_instance=RequestContext(request))

            elif Usuario.objects.get(nome=nome):
                messages.error(request, 'Nome de usuario ja cadastrado')
                return render_to_response('registro.html', {}, context_instance=RequestContext(request))
        except:
            new_usuario = Usuario(nome=nome, email=email, senha=senha)
            new_usuario.save()
            messages.success(request, 'Usuario criado com sucesso')
            return redirect('/')

# Função usada para Login do usuario
# Permite login tanto com nome, como com o email
def login(request):
    if request.method == 'GET':
        return redirect('/')
    elif request.method == 'POST':
        nome_ou_email = request.POST['nome_ou_email']
        senha = request.POST['senha']
        PADRAO_EMAIL = re.compile(
            r"^[A-Za-z0-9-_]+\.?[A-Za-z0-9-_]+?@[A-Za-z0-9-]+\.[A-Za-z0-9-]+?\.?[A-Za-z0-9-]+?\.?[A-Za-z0-9-]+?")
        PADRAO_NOME = re.compile(r"[A-Z]?[A-Za-z0-9]{4,100}")

        try:
            if PADRAO_EMAIL.match(nome_ou_email):
                usuario = Usuario.objects.get(email=nome_ou_email)
                if senha == usuario.senha:
                    request.session['email'] = usuario.email
                    request.session.set_expiry(86400)
                    return redirect('/app')
                else:
                    messages.error(request, 'Senha Incorreta')
            elif PADRAO_NOME.match(nome_ou_email):
                usuario = Usuario.objects.get(nome=nome_ou_email)
                if senha == usuario.senha:
                    request.session['email'] = usuario.email
                    request.session.set_expiry(86400)
                    return redirect('/app')
                else:
                    messages.error(request, 'Senha Incorreta')
            else:
                messages.error(request, 'Usuario invalido')
                return render_to_response('login.html', {}, context_instance=RequestContext(request))

            return redirect('/')
            # return render_to_response('login.html', {}, context_instance=RequestContext(request))
        except:
            messages.error(request, 'Usuario nao cadastrado')
            return redirect('/')
            # return render_to_response('login.html', {}, context_instance=RequestContext(request))
        
def app(request):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
        return render_to_response('app.html', {'usuario': usuario, 'usuarios': Usuario.objects.all(),
                                               'compartilhados': compartilhados},
                                  context_instance=RequestContext(request))
    except:
        return redirect('/')

# Função que permite visualizar a pasta renderizada
def view_pasta(request, id):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
        pasta = Pasta.objects.get(id=id)
        return render_to_response('view_pasta.html',
                                  {'usuario': usuario, 'pasta': pasta, 'usuarios': Usuario.objects.all(),
                                   'compartilhados': compartilhados},
                                  context_instance=RequestContext(request))
    except:
        return redirect('/')




# Função usada na visualização de arquivos compartilhados
def view_file_compartinhado(request, id):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        arquivo = Arquivo.objects.get(id=id)
        if request.method == 'GET':
            file = arquivo.arquivo
            file.open(mode='rb')
            content = file.readlines()
            file.close()
            return render_to_response('view_file_compartilhado.html',
                                      {'usuario': usuario, 'arquivo': arquivo, 'content': content,
                                       'usuarios': Usuario.objects.all()},
                                      context_instance=RequestContext(request))
    except:
        return redirect('/')

# Função que permite edição do arquivo compartilhado
# Onde é permitido alterar o nome, tipo, pasta, texto e exlcuir o arquivo compartilhado em modo "escrita"
def edit_arquivo_compartilhado(request, id):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        arquivo = Arquivo.objects.get(id=id)
        if request.method == 'GET':
            file = arquivo.arquivo
            file.open(mode='rb')
            content = file.readlines()
            file.close()
            return render_to_response('edit_file_compartilhado.html',
                                      {'usuario': usuario, 'arquivo': arquivo, 'content': content,
                                       'usuarios': Usuario.objects.all()},
                                      context_instance=RequestContext(request))
        elif request.method == 'POST':
            myfile = ContentFile(request.POST['content'])
            nome_arquivo = request.POST['nome']
            tipo_arquivo = request.POST['tipo']

            try:
                arq_temp = Arquivo.objects.get(nome=nome_arquivo)
                messages.error(request, 'Ja existe arquivo com este nome')
                return redirect('/app')
            except:
                arquivo.arquivo.save(str(nome_arquivo) + '.' + tipo_arquivo, myfile)
                arquivo.nome = nome_arquivo
                arquivo.tipo = tipo_arquivo
                arquivo.save()
                myfile.open(mode='rb')
                content = myfile.readlines()
                myfile.close()
                messages.success(request, 'Alterado com sucesso')
                return render_to_response('edit_file_compartilhado.html', {'arquivo': arquivo, 'content': content,
                                                                           'usuarios': Usuario.objects.all()},
                                          context_instance=RequestContext(request))
    except:
        return redirect('/')

# Função usada para criação de novos arquivos
def create_arquivo(request):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
        if request.method == 'GET':
            return render_to_response('create_file.html', {'usuario': usuario,
                                                           'usuarios': Usuario.objects.all(),
                                                           'compartilhados': compartilhados},
                                      context_instance=RequestContext(request))
        elif request.method == 'POST':
            nome = request.POST['nome']
            tipo = request.POST['tipo']
            if 'pasta' in request.POST:
                pasta = Pasta.objects.get(id=request.POST['pasta'])
            else:
                pasta = None
            try:
                arquivo_temp = Arquivo.objects.get(nome=nome)
                messages.error(request, 'Ja existe arquivo com este nome')
                return render_to_response('create_file.html', {'usuario': usuario,
                                                               'usuarios': Usuario.objects.all(),
                                                               'compartilhados': compartilhados},
                                          context_instance=RequestContext(request))
            except:
                try:
                    file = ContentFile(request.POST['content'])
                    arquivo = Arquivo(nome=nome, tipo=tipo, pasta=pasta)
                    arquivo.arquivo.save(nome + '.' + tipo, file)
                    arquivo.save()
                    usuario.arquivos.add(arquivo)
                    usuario.save()
                    messages.success(request, 'Arquivo adicionado com sucesso')
                    if pasta:
                        return redirect('/pasta/' + str(pasta.id))
                    else:
                        return redirect('/')
                except:
                    messages.error(request, 'Nao foi possivel criar novo arquivo')
                    return render_to_response('create_file.html', {'usuario': usuario,
                                                                   'usuarios': Usuario.objects.all(),
                                                                   'compartilhados': compartilhados},
                                              context_instance=RequestContext(request))
    except:
        return redirect('/')

# Função usada para editar um arquivo
# Podendo alterar o nome, tipo e pasta
def edit_arquivo(request, id):
    usuario = Usuario.objects.get(email=request.session['email'])
    arquivo = Arquivo.objects.get(id=id)
    if request.method == 'GET':
        file = arquivo.arquivo
        file.open(mode='rb')
        content = file.readlines()
        file.close()
        return render_to_response('edit_file.html', {'usuario': usuario, 'arquivo': arquivo, 'content': content,
                                                     'usuarios': Usuario.objects.all()},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        myfile = ContentFile(request.POST['content'])
        nome_arquivo = request.POST['nome']
        tipo_arquivo = request.POST['tipo']
        if 'pasta' in request.POST:
            pasta_arquivo = Pasta.objects.get(id=request.POST['pasta'])
        else:
            pasta_arquivo = None
        try:
            if nome_arquivo != arquivo.nome:
                arq_temp = Arquivo.objects.get(nome=nome_arquivo)
                messages.error(request, 'Ja existe arquivo com este nome')
                return redirect('/app')
            else:
                arq_temp = Arquivo.objects.get(id=nome_arquivo.id)

        except:
            arquivo.arquivo.save(str(nome_arquivo) + '.' + tipo_arquivo, myfile)
            arquivo.nome = nome_arquivo
            arquivo.pasta = pasta_arquivo
            arquivo.tipo = tipo_arquivo
            arquivo.save()
            myfile.open(mode='rb')
            content = myfile.readlines()
            myfile.close()
            messages.success(request, 'Alterado com sucesso')
            return render_to_response('edit_file.html', {'arquivo': arquivo, 'content': content,
                                                         'usuarios': Usuario.objects.all()},
                                      context_instance=RequestContext(request))

# Função usada para editar um pasta
# Podendo alterar titulo, nome e texto
def edit_pasta(request, id):
    usuario = Usuario.objects.get(email=request.session['email'])
    pasta = Pasta.objects.get(id=id)
    if request.method == 'GET':
        return render_to_response('edit_pasta.html', {'usuario': usuario, 'pasta': pasta},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        titulo_pasta = request.POST['titulo']
        descricao_pasta = request.POST['descricao']
        try:
            if titulo_pasta != pasta.titulo:
                pasta_temp = Pasta.objects.get(titulo=titulo_pasta)
                messages.error(request, 'Ja existe pasta com esse nome')
                return render_to_response('edit_pasta.html', {'usuario': usuario, 'pasta': pasta},
                                          context_instance=RequestContext(request))
            else:
                pasta_temp = Pasta.objects.get(id=titulo_pasta.id)
        except:
            pasta.titulo = titulo_pasta
            pasta.desc = descricao_pasta
            pasta.save()
            messages.success(request, 'Alterado com sucesso')
            return redirect('/app')

# Função usada para compartilhar um arquivo de escrita como leitura
def compartilhar_amigo(request, id):
    try:
        arquivo = Arquivo.objects.get(id=id)
        id_usuario = request.POST['id_usuario']
        usuario = Usuario.objects.get(id=id_usuario)
        if request.POST['habilitado'] == '1':
            habilitado = True
        else:
            habilitado = False
        comp = Compartilhado(usuario=usuario, arquivo=arquivo, habilitado=habilitado)
        comp.save()
        messages.success(request, 'Compartilhado com sucesso')
        return redirect('/app')
    except:
        return redirect('/')

# Função usada para notificar o usuario quando tiver arquivos compartilhados
def notificacoes(request):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
        for comp in compartilhados:
            comp.status = True
            comp.save()
        return render_to_response('notificacoes.html', {'usuario': usuario,
                                                        'usuarios': Usuario.objects.all(),
                                                        'compartilhados': compartilhados,
                                                        'compartilhados_cmg': Compartilhado.objects.filter(
                                                            usuario=usuario)},
                                  context_instance=RequestContext(request))
    except:
        return redirect('/')

# Função usada na criação de novas pastas
def nova_pasta(request):
    if request.method == 'GET':
        try:
            usuario = Usuario.objects.get(email=request.session['email'])
            compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
            return render_to_response('nova_pasta.html', {'usuario': usuario,
                                                          'usuarios': Usuario.objects.all(),
                                                          'compartilhados': compartilhados},
                                      context_instance=RequestContext(request))
        except:
            return redirect('/')
    elif request.method == 'POST':
        titulo = request.POST['titulo']
        descricao = request.POST['descricao']
        if 'pasta' in request.POST:
            past = Pasta.objects.get(id=request.POST['pasta'])
        else:
            past = None
        try:
            pasta_temp = Pasta.objects.get(titulo=titulo)
            messages.error(request, 'Ja existe pasta com esse nome')
            return render_to_response('nova_pasta.html', {}, context_instance=RequestContext(request))
        except:
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

# Função usada para excluir pasta
def remove_pasta(request, id):
    try:
        pasta = Pasta.objects.get(id=id)
        pasta.status = False
        pasta.save()
        for arq in pasta.arquivo_set.all():
            arq.status = False
            arq.save()
        messages.success(request, 'Pasta removida com sucesso')
    except:
        messages.error(request, 'Nao foi possivel remover a pasta')
    return redirect('/app')

# Função usada para definir a lixeira
def lixeira(request):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
        return render_to_response('lixeira.html', {'usuario': usuario,
                                                   'usuarios': Usuario.objects.all(),
                                                   'compartilhados': compartilhados},
                                  context_instance=RequestContext(request))
    except:
        return redirect('/')

# Função usada para remover aquivos
def remove_arquivo(request, id):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        arquivo = Arquivo.objects.get(id=id)
        pasta = arquivo.pasta
        arquivo.status = False
        arquivo.save()
        messages.success(request, 'Arquivo removido com sucesso')
        if pasta:
            return redirect('/pasta/' + str(pasta.id))
        else:
            return redirect('/')
    except:
        messages.error(request, 'Nao foi possivel remover o arquivo')
        return redirect('/')

# Função extra
# Função usada para importar um arquivo do tipo txt ou md para o seu repositorio de arquivos no sistema
def upload_arquivo(request):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
        if request.method == 'GET':
            return render_to_response('upload.html', {'usuario': usuario,
                                                      'usuarios': Usuario.objects.all(),
                                                      'compartilhados': compartilhados},
                                      context_instance=RequestContext(request))
        elif request.method == 'POST':
            try:
                nome = request.POST['nome']
                arquivo = request.FILES['file']
                tipo = request.POST['tipo']
                if 'pasta' in request.POST:
                    pasta = Pasta.objects.get(id=request.POST['pasta'])
                else:
                    pasta = None
                arquivo = Arquivo(nome=nome, tipo=tipo, arquivo=arquivo, pasta=pasta)
                arquivo.save()
                usuario.arquivos.add(arquivo)
                usuario.save()
                messages.success(request, 'Arquivo adicionado com sucesso')
                if pasta:
                    return redirect('/pasta/' + str(pasta.id))
                else:
                    return redirect('/')
            except:
                messages.error(request, 'Nao foi possivel adicionar arquivo')
                return redirect('/')
    except:
        return redirect('/')

# Função usada para sair do sistema
def logout(request):
    request.session.clear()
    return redirect('/')

# Função extra
# Função usada para restaurar pastas da lixeira
def restaurar_pasta(request, id):
    try:
        pasta = Pasta.objects.get(id=id)
        pasta.status = True
        pasta.save()
        for arq in pasta.arquivo_set.all():
            arq.status = True
            arq.save()
        messages.success(request, 'Pasta restaurada com sucesso')
    except:
        messages.error(request, 'Nao foi possivel restaurar a pasta')
    return redirect('/')

# Função extra
# Função usada para restaurar arquivos da lixeira
def restaurar_arquivo(request, id):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        arquivo = Arquivo.objects.get(id=id)
        pasta = arquivo.pasta
        arquivo.status = True
        arquivo.save()
        messages.success(request, 'Arquivo restaurado com sucesso')
        if pasta:
            return redirect('/pasta/' + str(pasta.id))
        else:
            return redirect('/')
    except:
        messages.error(request, 'Nao foi possivel restaurar o arquivo')
        return redirect('/')


# Função usada para excluir arquivos permanentemente da lixeira
def limpar_lixeira(request):
    try:
        pastas = Pasta.objects.filter(status=False)
        arquivos = Arquivo.objects.filter(status=False)
        for pasta in pastas:
            pasta.delete()

        for arquivo in arquivos:
            arquivo.delete()

        messages.success(request, 'Lixeira esvaziada com sucesso')
    except:
        messages.error(request, 'Nao foi possivel esvaziar lixeira')
    return redirect('/lixeira')