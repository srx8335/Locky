# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# AppConfig configuration made easy. Look inside private/appconfig.ini
# Auth is for authenticaiton and access control
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth
import os
import re
from datetime import datetime

REQUIRED_WEB2PY_VERSION = "2.27.1"

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

web2py_version_string = request.global_settings.web2py_version.split("-")[0]
web2py_version = list(map(int, web2py_version_string.split(".")[:3]))
if web2py_version < list(map(int, REQUIRED_WEB2PY_VERSION.split(".")[:3])):
    raise HTTP(500, f"Requires web2py version {REQUIRED_WEB2PY_VERSION} or newer, not {web2py_version_string}")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
configuration = AppConfig(reload=True)

locky_ntfy_topic = os.getenv("LOCKY_NTFY_TOPIC") or configuration.get("notifications.ntfy_topic")
locky_tally_form_url = os.getenv("LOCKY_TALLY_FORM_URL") or configuration.get("tally.form_url")
locky_pusher_key = os.getenv("LOCKY_PUSHER_KEY") or configuration.get("pusher.key")
locky_pusher_cluster = os.getenv("LOCKY_PUSHER_CLUSTER") or configuration.get("pusher.cluster")

if "GAE_APPLICATION" not in os.environ:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(configuration.get("db.uri"),
             pool_size=configuration.get("db.pool_size"),
             migrate_enabled=configuration.get("db.migrate"),
             check_reserved=["all"])
else:
    # ---------------------------------------------------------------------
    # connect to Google Firestore
    # ---------------------------------------------------------------------
    db = DAL("firestore")
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be "controller/function.extension"
# -------------------------------------------------------------------------
response.generic_patterns = [] 
if request.is_local and not configuration.get("app.production"):
    response.generic_patterns.append("*")

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = "bootstrap4_inline"
response.form_label_separator = ""

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = "concat,minify,inline"
# response.optimize_js = "concat,minify,inline"

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = "0.0.0"

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=configuration.get("host.names"))

# -------------------------------------------------------------------------
# create all tables needed by auth, maybe add a list of extra fields
# -------------------------------------------------------------------------
auth.settings.extra_fields["auth_user"] = [Field('rfid', 'string')]
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = "logging" if request.is_local else configuration.get("smtp.server")
mail.settings.sender = configuration.get("smtp.sender")
mail.settings.login = configuration.get("smtp.login")
mail.settings.tls = configuration.get("smtp.tls") or False
mail.settings.ssl = configuration.get("smtp.ssl") or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------  
# read more at http://dev.w3.org/html5/markup/meta.name.html               
# -------------------------------------------------------------------------
response.meta.author = configuration.get("app.author")
response.meta.description = configuration.get("app.description")
response.meta.keywords = configuration.get("app.keywords")
response.meta.generator = configuration.get("app.generator")
response.show_toolbar = configuration.get("app.toolbar")

# -------------------------------------------------------------------------
# your http://google.com/analytics id                                      
# -------------------------------------------------------------------------
response.google_analytics_id = configuration.get("google.analytics_id")

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
if configuration.get("scheduler.enabled"):
    from gluon.scheduler import Scheduler
    scheduler = Scheduler(db, heartbeat=configuration.get("scheduler.heartbeat"))

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table("mytable", Field("myfield", "string"))
#
# Fields can be "string","text","password","integer","double","boolean"
#       "date","time","datetime","blob","upload", "reference TABLENAME"
# There is an implicit "id integer autoincrement" field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield="value")
# >>> rows = db(db.mytable.myfield == "value").select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------


db.auth_user._format = '%(first_name)s %(last_name)s'


db.define_table('chaveiro',
    Field('rfid', 'string'),
    Field('descricao_chaveiro', 'string', requires=[IS_MATCH('^[A-Za-zÀ-ÿ ]+$', error_message='O nome só pode conter letras e espaços')],label='Designação do Chaveiro:'),
    format='%(descricao_chaveiro)s')

# Show the ID but do not allow editing.
# Mostrar o ID mas não permitir a edição.
db.chaveiro.id.readable = True
db.chaveiro.id.writable = False
db.chaveiro.id.label = 'ID do Chaveiro:'

for field in db.chaveiro.fields:
        db.chaveiro[field].requires = IS_NOT_EMPTY(error_message="Campo obrigatório")


data_atual = datetime.now()

data_atual = data_atual.strftime('%Y-%m-%d %H:%M:%S')






db.define_table('emprestimo',
    Field('id_chaveiro', 'reference chaveiro', label='Chaveiro Requisitado:'),
    Field('nome_empregado', 'string', requires=[IS_MATCH('^[A-Za-zÀ-ÿ ]+$', error_message='O nome só pode conter letras e espaços')], label='Nome do/a Colaborador/a (requisição):'),
    Field('grupo_colaborador', 'string', readable=False, writable=False, label='Grupo do colaborador'),
    Field('data_requisicao', 'datetime', default= data_atual, label='Data de Requisição:'),
    Field('data_devolucao', 'datetime', label='Data de Devolução:'),
    Field('nome_devolucao', 'string', label='Nome do/a Colaborador/a (devolução):'),
    Field('obs', 'string', default='N/A', label='Observações:'))




exceptions = ['data_devolucao', 'obs', 'nome_devolucao']

for field in db.emprestimo.fields:
    if field not in exceptions:
        db.emprestimo[field].requires = IS_NOT_EMPTY(error_message="Campo obrigatório")




db.define_table('feedback_chaves',
    Field('email'),
    Field('melhorias', 'text'),
    Field('comentarios_equipe', 'text'),
    Field('avaliacao_final', 'integer'),

    # Matrix ratings (one column for each aspect).
    # Avaliações em matriz (uma coluna para cada aspeto).
    Field('aspeto_programa'),
    Field('experiencia_utilizacao'),
    Field('disposicao_elementos'),
    Field('linguagem_termos'),
    Field('facilidade_tarefas'),
    Field('facilidade_info'),

    Field('data_recebido', 'datetime', default=request.now)
)





# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
