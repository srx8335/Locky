# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------



page = request.function

response.menu += [
    (T('Listar Requisições'), page == 'listar_emprestimos', URL('default', 'listar_emprestimos'),[
        (T('Adicionar Requisição'), page == 'add_emprestimo', URL('default', 'add_emprestimo'))
        ])
    ]





page = request.function

response.menu += [
    (T('Listar Chaveiros'), page == 'listar_chaveiros', URL('default', 'listar_chaveiros'),[
        (T('Adicionar Chaveiro'), page == 'add_chaveiro', URL('default', 'add_chaveiro'))
        ])
    ]


response.menu += [
    (T('Calendário Requisições'), page == 'cal', URL('default', 'cal'), [('', False, '', [], {'_class': 'sem-bullet'})])
]


if auth.has_membership('admin'):
    response.menu += [
        (
            T('Feedback dos Utilizadores'),
            page == 'respostas_formulario',
            URL('default', 'respostas_formulario'),
            [
                ('', False, '', [], {'_class': 'sem-bullet'})
            ]
        )
    ] 
# # Check whether the user is authenticated and belongs to the "admin" group.
# # Verifica se o utilizador está autenticado e pertence ao grupo "admin".
# if auth.user and auth.has_membership('admin'):




response.menu += [
    (T('Deixe o seu Feedback!'), page == 'formulario', URL('default', 'formulario'), [('', False, '', [], {'_class': 'sem-bullet'})])
]




# page = request.function

# response.menu += [
#     (T('Listar Empregados'), page == 'listar_empregados', URL('default', 'listar_empregados'),[
#         (T('Adicionar Empregado'), page == 'add_empregado', URL('default', 'add_empregado'))
#         ])
#     ]

# ----------------------------------------------------------------------------------------------------------------------
# provide shortcuts for development. you can remove everything below in production
# ----------------------------------------------------------------------------------------------------------------------


