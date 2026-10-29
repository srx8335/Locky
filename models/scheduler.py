# from gluon.scheduler import Scheduler
# from datetime import datetime, date, time

# scheduler = Scheduler(db)

# def verificar_chaves_em_aberto():
#     hoje = date.today()
#     emprestimos = db(
#         (db.emprestimos.data_inicio <= hoje) &
#         (db.emprestimos.data_devolucao == None)
#     ).select()

#     for e in emprestimos:
#         utilizador = db.utilizadores(e.utilizador_id)
#         mensagem = f"""
#         Hello {utilizador.nome},
#         Olá {utilizador.nome},

#         We detected that you have not returned the key "{e.nome_chave}" borrowed on {e.data_inicio}.
#         Detetámos que ainda não devolveste a chave "{e.nome_chave}" que levantaste no dia {e.data_inicio}.
#         Please return it as soon as possible.
#         Por favor, devolve-a o mais breve possível.

#         Thank you!
#         Obrigado!
#         """
#         mail.send(
#             to=utilizador.email,
#             subject="Chave por devolver",
#             message=mensagem
#         )

# # Schedule the task.
# # Agendar a tarefa.
# scheduler.queue_task(
#     verificar_chaves_em_aberto,
#     start_time=datetime.combine(date.today(), time(23, 59)),
#     repeat_interval=86400
# )
