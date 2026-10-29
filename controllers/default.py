# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

import requests
import os
from applications.Locky.private import pusher_client
from applications.Locky.private import acessos
from gluon import *
from gluon import current
import csv
import json

NTFY_TOPIC = os.getenv("LOCKY_NTFY_TOPIC") or configuration.get("notifications.ntfy_topic")



# ---- example index page ----
def index():
    redirect(URL('default', 'user', args='login'))

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """

    if auth.is_logged_in():
        redirect(URL('default', 'dashboard_init'))

    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)



def dashboard_init():
    response.files.append(URL('static', 'css/dashboard.css'))
    response.files.append(URL('static', 'css/menu_lateral.css'))

    return dict()

# Visual separator for table links.
# Separador visual para os links das tabelas.

def separador(row):
        return SPAN(' | ', _class='separador')

# -----KEY MANAGEMENT ACTIONS----------------------------------------------------------------------------------------------------------------------------------
# -----AÇÕES DE CHAVES----------------------------------------------------------------------------------------------------------------------------------------

# ---- list keys ----
# ---- listar chaves ----
@auth.requires_login()
def listar_chaveiros():

    def link_editar(row):
        return A('Editar', _href=URL('default', 'editar_chaveiro', args=[row.id]), _class='btn_edit')

    def link_apagar(row):
        return A('Excluir', _href=URL('default', 'apagar_chaveiro', args=[row.id]), _class='apagar')

# Make the key text red when it is unavailable.
# Coloca o texto da chave a vermelho quando não está disponível.
    def formatar_descricao(value, row):
        emprestimo_ativo = db(
            (db.emprestimo.id_chaveiro == row.id) &
            (db.emprestimo.data_devolucao == None)
        ).select().first()

        if emprestimo_ativo:
            return XML(f'<span style="color: red;">{value}</span>')
        else:
            return value

    links = []
    if auth.has_membership('admin'):
        links = [link_editar, separador, link_apagar]

    # Add CSS.
    # Adiciona CSS.
    response.files.append(URL('static', 'css/listar.css'))
    response.files.append(URL('static', 'css/menu_lateral.css'))

    db.chaveiro.descricao_chaveiro.represent = formatar_descricao

    # SmartGrid.
    grid = SQLFORM.smartgrid(
        db.chaveiro,
        showbuttontext=False,
        linked_tables=[],
        links=links,
        csv=False,
        searchable=True,
        editable=False,
        deletable=False,
        create=False,
        details=False,
        user_signature=False,
    )

# Return is_admin to show or hide actions.
# Devolve is_admin para mostrar ou esconder ações.
    return dict(grid=grid, is_admin=auth.has_membership('admin'))
















# ---- add key form ----
# ---- formulário para adicionar uma chave ----
@auth.requires_login()
def add_chaveiro():
    response.files.append(URL('static', 'css/form.css'))
    response.files.append(URL('static', 'css/menu_lateral.css'))

    form = SQLFORM(db.chaveiro)


    # Custom buttons.
    # Botões personalizados.
    botao_voltar = A('<- Voltar', _href=URL('default', 'listar_chaveiros'), _class='btnVoltar')
    submit_btn = form.element('input', _type='submit')
    if submit_btn:
        submit_btn['_value'] = 'Adicionar Chaveiro'
        submit_btn['_class'] = 'btnSubmit'

    form.append(DIV(botao_voltar, submit_btn, _class='botao-container'))

    if form.process().accepted:
        chaveiro = form.vars

# Notifications.
# Notificações.
        requests.post(
            NTFY_TOPIC,
            headers={"Priority": "5"},
            data=f"🔑🆕 Chaveiro Criado {chaveiro.id} {chaveiro.descricao_chaveiro}".encode('utf-8')
        )
    else:
        chaveiro = None

    return dict(form=form, chaveiro=chaveiro)





# ---- edit key ----
# ---- editar chave ----
@auth.requires_login()
def editar_chaveiro():
    response.files.append(URL('static', 'css/form.css'))
    response.files.append(URL('static', 'css/menu_lateral.css'))
    chaveiro_id = request.args(0) or redirect(URL('listar_chaveiros'))

    form = SQLFORM(db.chaveiro, chaveiro_id, showid=True).process()
     
        
    botao_voltar = A('<- Voltar', _href=URL('default', 'listar_chaveiros'), _class='btnVoltar')

    # Customize form button attributes.
    # Personaliza os atributos dos botões do formulário.
    submit_btn = form.element('input', _type='submit')
    if submit_btn:
            submit_btn['_value'] = 'Editar Chaveiro'
            submit_btn['_class'] = 'btnSubmit'
    
    botao_container = DIV(botao_voltar, submit_btn, _class='botao-container')

    form.append(botao_container)  # adicionar os botões ao formulário





    if form.accepted:
        chaveiro = form.vars

        requests.post(NTFY_TOPIC, headers={"Priority": "5"},
            data=f"🔑📝 Chaveiro Editado \n\n New Info: {chaveiro.id} -> {chaveiro.descricao_chaveiro}".encode(encoding='utf-8'))
        redirect(URL('listar_chaveiros'))


        response.flash = 'Chaveiro editado com sucesso!'
        redirect(URL('listar_chaveiros'))
    elif form.errors:
        response.flash = 'Não foi possível editar o chaveiro.'

    return dict(form=form)


# ---- delete key ----
# ---- apagar chave ----
@auth.requires_login()
def apagar_chaveiro():
    chaveiro_id = request.args(0)

    chaveiro = db.chaveiro(chaveiro_id)

    if chaveiro_id:
        deleted = db(db.chaveiro.id == chaveiro_id).delete()
        if deleted == 1:
            requests.post(NTFY_TOPIC, headers={"Priority": "5"},
            data=f"🔑🗑️ Chaveiro Apagado {chaveiro.id} {chaveiro.descricao_chaveiro}".encode(encoding='utf-8'))
        redirect(URL('listar_chaveiros'))
    else:
        redirect(URL('listar_chaveiros'))
        response.flash = "Não foi possível apagar o chaveiro."







# -----LOAN ACTIONS--------------------------------------------------------------------------------------------------------------------------------------------- 
# -----AÇÕES DE EMPRÉSTIMOS--------------------------------------------------------------------------------------------------------------------------------------
# ---- list loans ----
# ---- listar empréstimos ----
@auth.requires_login()
def listar_emprestimos():

    def link_checkbox(row):
        # Create a checkbox with name="chk" and value=row.id.
        # Cria uma checkbox com name="chk" e value=row.id.
        return INPUT(_type='checkbox', _name='selecionados', _value=row.id)
    
    def link_editar(row):
        return A('Editar', _href=URL('default', 'editar_emprestimo', args=[row.id]), _class='btn_edit_emp')
    
    def link_devolver(row):
        return A('Devolver', _href="#", _class='devolver_emprestimo', **{'_data-id': row.id})
    
    def link_apagar(row):
        if auth.has_membership('admin'):
            return A('Excluir', _href=URL('default', 'apagar_emprestimo', args=[row.id]), _class='apagar_emp')
        else:
            return None


# Format loan dates and highlight loans that are still open.
# Formata as datas dos empréstimos e destaca os que ainda estão abertos.
    def destacar_data_formatada(valor, row):
        if isinstance(valor, datetime):
            valor_formatado = valor.strftime('%Y-%m-%d %H:%M')
        else:
            valor_formatado = str(valor)  # fallback

        if not row.data_devolucao:
            return XML(f'<span style="color: red;">{valor_formatado}</span>')
        
        return valor_formatado



    def destacar_emprestimo(valor, row):
        if not row.data_devolucao :  # Se ainda não foi devolvido
            return XML(f'<span style="color: red;">{valor}</span>')
        return valor



    response.files.append(URL('static', 'css/listar.css'))
    response.files.append(URL('static', 'css/menu_lateral.css'))

    db.emprestimo.id.represent = destacar_emprestimo
    db.emprestimo.nome_empregado.represent = destacar_emprestimo
    db.emprestimo.data_requisicao.represent = destacar_data_formatada
    db.emprestimo.data_devolucao.represent = destacar_data_formatada
    db.emprestimo.obs.represent = destacar_emprestimo


    grid = SQLFORM.smartgrid(
    db.emprestimo,
    showbuttontext=False,
    linked_tables=[],
    links=[link_checkbox,link_editar, link_devolver, link_apagar],
    csv=False,
    searchable=True,
    editable=False,
    deletable=False,
    create=False,
    details=False,
    user_signature=False,
)
    return dict(grid=grid)




@auth.requires_login()
def add_emprestimo():
    response.files.append(URL('static', 'css/form.css'))
    response.files.append(URL('static', 'css/menu_lateral.css'))

    db.emprestimo.id_chaveiro.widget = SQLFORM.widgets.autocomplete(
        request,
        db.chaveiro.descricao_chaveiro,
        id_field=db.chaveiro.id,
        min_length=1
    )

    form = SQLFORM(db.emprestimo)

    form.insert(-1, INPUT(_type='hidden', _name='grupo_colaborador', _id='grupo_colaborador'))

    

    # Customize buttons.
    # Personalização dos botões.
    botao_voltar = A('<- Voltar', _href=URL('default', 'listar_emprestimos'), _class='btnVoltar')
    submit_btn = form.element('input', _type='submit')
    if submit_btn:
        submit_btn['_value'] = 'Requisitar'
        submit_btn['_class'] = 'btnSubmit'
    botao_container = DIV(botao_voltar, submit_btn, _class='botao-container')
    form.append(botao_container)



    formulario = form.process(onvalidation=validar_acesso)

    if formulario.accepted:
        # Use processed.vars.grupo_colaborador, not the 'grupo' variable, which does not exist here.
        # Usa processed.vars.grupo_colaborador, não a variável 'grupo', que não existe aqui.
        db.emprestimo[formulario.vars.id] = dict(grupo_colaborador=formulario.vars.grupo_colaborador)
        print("Formulário aceite:", formulario.vars)
        requests.post(NTFY_TOPIC, headers={"Priority": "5"},
            data=f"🔐📝 Requisição Criada \n\n ID Requisição -> ID Chaveiro: {form.vars.id} -> {form.vars.id_chaveiro}".encode(encoding='utf-8'))
        redirect(URL('listar_emprestimos'))

    elif formulario.errors:
        print("Erros no formulário:", formulario.errors)
        response.flash = 'Há erros no formulário.'

    print("Vars recebidas:", form.vars)
    return dict(form=form)

















# Helper function for sending events to Pusher.
# Função auxiliar para enviar eventos para o Pusher.
def enviar_trigger_pusher(tipo, valor):
    pusher_client.trigger('chaveiro', tipo, {tipo: valor})
    print(f"Trigger enviado com {tipo}: {valor}")


def get_nome_chave():
    print("Função get_nome_chave chamada")
    rfid = request.vars.id
    print(f"RFID recebido: {rfid}")

    if not rfid:
        return dict(erro="ID não recebido")

    chave = db(db.chaveiro.rfid == rfid).select().first()
    if chave:
        enviar_trigger_pusher('chave', chave.id)
        print(f"Chave encontrada: {chave.id}")
        # Send the key ID to Pusher.
        # Envia o ID da chave para o Pusher.
        return dict(chave=chave.id)
    else:
        return dict(erro="ID não corresponde a chave")





def get_nome_colaborador():
    nome_colab = request.vars.nome or "Desconhecido"
    grupo_colab = request.vars.grupo or "Desconhecido"

    # Send both values through Pusher (name + group).
    # Envia ambos através do Pusher (nome + grupo).
    enviar_trigger_pusher('colaborador', {
        'nome': nome_colab,
        'grupo': grupo_colab
    })

    return dict(nome_colab=nome_colab, grupo_colab=grupo_colab)


def validar_acesso(form):
    grupo = form.vars.grupo_colaborador
    id_chave = form.vars.id_chaveiro

    print(f"Grupo recebido: {grupo}, Chave: {id_chave}")
    print(f"Grupo bruto recebido: {repr(form.vars.grupo_colaborador)}")

    if not grupo or not id_chave:
        form.errors.id_chaveiro = "Grupo ou chave não definidos."
        return

    if grupo not in acessos.grupos_acessos:
        form.errors.id_chaveiro = "Grupo sem permissões definidas."
        return

    if int(id_chave) not in acessos.grupos_acessos[grupo]:
        form.errors.id_chaveiro = "O colaborador não tem permissão para requisitar esta chave."
        return















# ---- edit loan ----
# ---- editar empréstimo ----
@auth.requires_login()
def editar_emprestimo():
    response.files.append(URL('static', 'css/form.css'))
    response.files.append(URL('static', 'css/menu_lateral.css'))

    id_emprestimo = request.args(0) or redirect(URL('listar_emprestimos'))
    registro = db.emprestimo(id_emprestimo)

    form = SQLFORM(db.emprestimo, id_emprestimo, showid=False)

    form.insert(-1, INPUT(
        _type='hidden',
        _name='grupo_colaborador',
        _id='grupo_colaborador',
        _value=registro.grupo_colaborador or ""
    ))

    botao_voltar = A('<- Voltar', _href=URL('default', 'listar_emprestimos'), _class='btnVoltar')
    submit_btn = form.element('input', _type='submit')
    if submit_btn:
        submit_btn['_value'] = 'Editar Requisição'
        submit_btn['_class'] = 'btnSubmit'
    form.append(DIV(botao_voltar, submit_btn, _class='botao-container'))

    formulario = form.process(onvalidation=validar_acesso)

    if formulario.accepted:
        db.emprestimo[formulario.vars.id] = dict(grupo_colaborador=formulario.vars.grupo_colaborador)
        print("Formulário aceite:", formulario.vars)

        requests.post(NTFY_TOPIC, headers={"Priority": "5"},
            data=f"🔐📝 Requisição Editada \n\n ID Requisição -> ID Chaveiro: {form.vars.id} -> {form.vars.id_chaveiro}".encode(encoding='utf-8'))

        redirect(URL('listar_emprestimos'))

    elif formulario.errors:
        print("Erros no formulário:", formulario.errors)
        response.flash = 'Há erros no formulário.'

    print("Vars recebidas:", formulario.vars)
    return dict(form=formulario)








# ---- delete loan ----
# ---- apagar empréstimo ----
@auth.requires_login()
def apagar_emprestimo():
    emprestimo_id = request.args(0)

    emprestimo = db.emprestimo(emprestimo_id)

    if emprestimo_id:
        deleted = db(db.emprestimo.id == emprestimo_id).delete()
        if deleted == 1:
            requests.post(NTFY_TOPIC, headers={"Priority": "5"},
            data=f"🔐🗑️ Emprestimo Apagado.: {emprestimo.id}".encode(encoding='utf-8'))
        redirect(URL('listar_emprestimos'))
    else:
        redirect(URL('listar_emprestimos'))
        response.flash = "Não foi possível apagar o emprestimo."


@auth.requires_login()
def devolver_selecionados():
    ids = request.post_vars.getlist('ids[]')  # lista de ids selecionados
    nome = request.post_vars.get('nome')      # nome de quem devolve

    if not ids:
        return response.json(dict(status="erro", mensagem="Nenhum empréstimo selecionado"))

    for emp_id in ids:
        emprestimo = db.emprestimo(emp_id)
        if emprestimo:
            emprestimo.update_record(
                nome_devolucao=nome,    # campo que deves ter na tabela
                data_devolucao=request.now
            )
            # Send a notification for each loan.
            # Envia uma notificação para cada empréstimo.
            requests.post(
                NTFY_TOPIC,
                headers={"Priority": "5"},
                data=f"🔐📥 Emprestimo fechado (chave devolvida): {emprestimo.id}".encode('utf-8')
            )

    return ()


@auth.requires_login()
def fechar_emprestimo():
    emprestimo_id = request.args(0)
    nome_devolucao = request.vars.nome or "Desconhecido"  # vem do popup ou input

    emprestimo = db.emprestimo(emprestimo_id)

    emprestimo.update_record(
        nome_devolucao=nome_devolucao,
        data_devolucao=request.now
    )

    requests.post(
        NTFY_TOPIC,
        headers={"Priority": "5"},
        data=f"🔐📥 Emprestimo fechado (chave devolvida): {emprestimo.id}".encode('utf-8')
    )

    redirect(URL('listar_emprestimos'))


@auth.requires_login()
# Close the loan from the calendar.
# Fechar o empréstimo através do calendário.
def fechar_emprestimo_cal():
    emprestimo_id = request.args(0)

    emprestimo = db.emprestimo(emprestimo_id)

    emprestimo.update_record(
        data_devolucao=request.now
    )

    requests.post(NTFY_TOPIC, headers={"Priority": "5"},
            data=f"🔐📥 Emprestimo fechado (chave devolvida): {emprestimo.id}".encode(encoding='utf-8'))

    redirect(URL('cal'))



# -----EMPLOYEE ACTIONS-----------------------------------------------------------------------------------------------------------------------------------------
# -----AÇÕES DE COLABORADORES-----------------------------------------------------------------------------------------------------------------------------------
# ---- list employees ----
# ---- listar colaboradores ----
# @auth.requires_login()
# def listar_empregados():
#     def link_editar(row):
#         return A('Editar', _href=URL('default', 'editar_empregado', args=[row.id]), _class='btn_edit')
    
#     def link_apagar(row):
#         return A('Excluir', _href=URL('default', 'apagar_empregado', args=[row.id]), _class='apagar')

#     def separador(row):
#         return SPAN(' | ', _class='separador')


#     response.files.append(URL('static', 'css/listar.css'))
#     response.files.append(URL('static', 'css/menu_lateral.css'))
#     grid = SQLFORM.smartgrid(
#     db.empregado,
#     showbuttontext=False,
#     linked_tables=[],
#     links=[link_editar, separador, link_apagar],
#     csv=False,
#     searchable=True,
#     editable=False,
#     deletable=False,
#     create=False,
#     details=False,
#     user_signature=False,
# )
#     return dict(grid=grid)
    


# ---- add employee ----
# ---- adicionar colaborador ----
# @auth.requires_login()
# def add_empregado():
#     response.files.append(URL('static', 'css/form.css'))
#     response.files.append(URL('static', 'css/menu_lateral.css'))
#     form = SQLFORM(db.empregado).process()


#     # Customize form button attributes.
#     # Personaliza os atributos dos botões do formulário.
#     submit_btn = form.element('input', _type='submit')
#     if submit_btn:
#         submit_btn['_value'] = 'Adicionar Empregado'
#         submit_btn['_class'] = 'btnSubmit' 
        
#     botao_voltar = A('<- Voltar', _href=URL('default', 'listar_empregados'), _class='btnVoltar')
#     form.append(botao_voltar)  # Add a button at the end.
#     # Adiciona um botão no fim.


#     if form.accepted:
#         empregado = form.vars

#         requests.post(NTFY_TOPIC, headers={"Priority": "5"},
#             data=f"👤🆕 Empregado Adicionado {empregado.id} {empregado.nome_empregado}".encode(encoding='utf-8'))
#         redirect(URL('listar_empregados'))
#     else:
#         empregado = None
#     return dict(form=form, empregado=empregado)




# ---- edit employee ----
# ---- editar colaborador ----
# @auth.requires_login()
# def editar_empregado():
#     response.files.append(URL('static', 'css/form.css'))
#     response.files.append(URL('static', 'css/menu_lateral.css'))
#     id_emp = request.args(0)
    
#     form = SQLFORM(db.empregado, id_emp, showid=False).process()


#     # Customize form button attributes.
#     # Personaliza os atributos dos botões do formulário.
#     submit_btn = form.element('input', _type='submit')
#     if submit_btn:
#         submit_btn['_value'] = 'Editar Empregado'
#         submit_btn['_class'] = 'btnSubmit' 
        
#     botao_voltar = A('<- Voltar', _href=URL('default', 'listar_empregados'), _class='btnVoltar')
#     form.append(botao_voltar)  # Add a button at the end.
#     # Adiciona um botão no fim.


#     if form.accepted:
#         empregado = form.vars

#         requests.post(NTFY_TOPIC, headers={"Priority": "5"},
#             data=f"👤📝 Empregado Editado \n\n Nova Info.: {empregado.id} -> {empregado.nome_empregado}".encode(encoding='utf-8'))
#         redirect(URL('listar_empregados'))


#         response.flash = 'Empregado editado com sucesso!'
#         redirect(URL('listar_empregados'))
#     elif form.errors:
#         response.flash = 'Não foi possível editar o empregado.'
    
#     return dict(form=form, id_emp=id_emp)

# ---- delete employee ----
# ---- apagar colaborador ----
# @auth.requires_login()
# def apagar_empregado():
#     id_emp = request.args(0)

#     empregado = db.empregado(id_emp)

#     if id_emp:
#         deleted = db(db.empregado.id == id_emp).delete()
#         if deleted == 1:
#             requests.post(NTFY_TOPIC, headers={"Priority": "5"},
#             data=f"👤🗑️ Empregado Apagado:\n\n {empregado.id} -> {empregado.nome_empregado}".encode(encoding='utf-8'))
#         redirect(URL('listar_empregados'))
#     else:
#         redirect(URL('listar_empregados'))
#         response.flash = "Não foi possivel apagar o empregado"




# imp
def teste_print():
    nome = request.vars.nome or "Desconhecido"  

    # Send a WebSocket event with the received name.
    # Envia um evento WebSocket com o nome recebido.
    pusher_client.trigger('chaveiro', 'geral', {'nome': nome})
    print("Trigger enviado com nome:", nome)

    # Return a simple page.
    # Devolve uma página simples.
    return dict(nome=nome)


# FullCalendar integration.
# Integração com o FullCalendar.
@auth.requires_login()
def cal():
    response.files.append(URL('static', 'css/calendar.css'))

    return dict()
@auth.requires_login()
def eventos():
    emprestimos = db(
        db.emprestimo
    ).select(
        db.emprestimo.ALL,
        db.chaveiro.id,
        db.chaveiro.descricao_chaveiro,
        left=[
            db.chaveiro.on(db.emprestimo.id_chaveiro == db.chaveiro.id),
        ]
    )



    lista_eventos = []

    for emp in emprestimos:

        evento = dict(
            id_emprestimo=emp.emprestimo.id,
            title=f"{emp.emprestimo.nome_empregado} - {emp.chaveiro.descricao_chaveiro if emp.chaveiro else 'Sem chave'}",
            start=emp.emprestimo.data_requisicao.isoformat(),
            end=emp.emprestimo.data_devolucao.isoformat() if emp.emprestimo.data_devolucao else None,
            
            # Purple when returned; red when still open.
            # Roxo quando devolvido; vermelho quando ainda está aberto.
            color="#41045B" if emp.emprestimo.data_devolucao else "#be1f2d",

            # Additional data:
            # Dados adicionais:
            chave_id=emp.chaveiro.id if emp.chaveiro else None,
            chave_desc=emp.chaveiro.descricao_chaveiro if emp.chaveiro else "Desconhecida",
            empregado=emp.emprestimo.nome_empregado,
            data_req=emp.emprestimo.data_requisicao.strftime("%d/%m/%Y %H:%M"),
            nome_devolucao =emp.emprestimo.nome_devolucao if emp.emprestimo.nome_devolucao else "Ainda não devolvido",
            data_dev=emp.emprestimo.data_devolucao.strftime("%d/%m/%Y %H:%M") if emp.emprestimo.data_devolucao else "Ainda não devolvido"
        )

        # Mark the event as "open" when it has not been returned yet.
        # Marca o evento como "aberto" quando ainda não foi devolvido.
        if not emp.emprestimo.data_devolucao:
            evento['display'] = 'block'
            

        lista_eventos.append(evento)

    return response.json(lista_eventos)





# Feedback form.
# Formulário de satisfação.


def formulario():
    response.files.append(URL('static', 'css/menu_lateral.css'))
    return dict()
    
@request.restful()
def receber_form():
    def POST():
        import json
        dados = json.loads(request.body.read())
        campos = dados.get("data", {}).get("fields", [])

        valores = {}
        matriz = None

        for campo in campos:
            label = (campo.get("label") or "").strip()
            valor = campo.get("value")
            tipo = campo.get("type")

            if "E-mail" in label:
                valores["email"] = valor
            elif "melhorada" in label:
                valores["melhorias"] = valor
            elif "comentários" in label.lower() or "comentarios" in label.lower():
                valores["comentarios_equipe"] = valor
            elif tipo == "RATING":
                valores["avaliacao_final"] = valor
            elif tipo == "MATRIX":
                matriz = campo

        # Process the matrix.
        # Processa a matriz.
        if matriz:
            linhas = {row["id"]: row["text"] for row in matriz["rows"]}
            colunas = {col["id"]: col["text"] for col in matriz["columns"]}
            respostas = matriz["value"]

            mapa = {
                "Aspeto do programa": "aspeto_programa",
                "Experiência de Utilização": "experiencia_utilizacao",
                "Disposição dos elementos": "disposicao_elementos",
                "Linguagem/Termos Utilizados": "linguagem_termos",
                "Facilidade para realizar tarefas (ex.: registar uma requisição)": "facilidade_tarefas",
                "Facilidade para encontrar informações (ex.: chaves não entregues, nome das chaves)": "facilidade_info"
            }

            for linha_id, resposta in respostas.items():
                texto_linha = linhas.get(linha_id)
                nome_campo = mapa.get(texto_linha)
                id_coluna = resposta[0] if resposta else None
                texto_coluna = colunas.get(id_coluna, "Sem resposta")

                if nome_campo:
                    valores[nome_campo] = texto_coluna

        feedback_id = db.feedback_chaves.insert(**valores)
        return dict(status="sucesso", feedback_id=feedback_id)

    return locals()


@auth.requires_membership('admin')
def respostas_formulario():


    def link_editar(row):
        return A('Editar', _href=URL('default', 'editar_chaveiro', args=[row.id]), _class='btn_edit')

    def link_apagar(row):
        return A('Excluir', _href=URL('default', 'apagar_chaveiro', args=[row.id]), _class='apagar')
    
    links = []
    if auth.has_membership('admin'):
        links = [link_editar, separador, link_apagar]

    # Add CSS.
    # Adiciona CSS.
    response.files.append(URL('static', 'css/listar.css'))
    response.files.append(URL('static', 'css/menu_lateral.css'))

    # SmartGrid
    grid = SQLFORM.smartgrid(
        db.feedback_chaves,
        showbuttontext=False,
        linked_tables=[],
        links=links,

        user_signature=False,


        editable=False,
        deletable=False,

    )

    return dict(grid=grid)


