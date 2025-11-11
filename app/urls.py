from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name='app'

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),

    # Tarefas
    path('nova_tarefa/', views.nova_tarefa, name='nova_tarefa'),
    path('detalhar_tarefa/<int:tarefa_id>/', views.detalhar_tarefa, name='detalhar_tarefa'),
    path('minhas_tarefas/', views.minhas_tarefas, name='minhas_tarefas'),
    path('tarefas/<int:ano>/<int:mes>/<int:dia>/', views.tarefas_do_dia, name='tarefas_do_dia'),
    path('editar_tarefa/<int:tarefa_id>/', views.editar_tarefa, name='editar_tarefa'),
    path('excluir_tarefa/<int:tarefa_id>/', views.excluir_tarefa, name='excluir_tarefa'),
    path('marcar_concluida/<int:tarefa_id>/', views.marcar_concluida, name='marcar_concluida'),
    path('alterar_status_tarefa/<int:tarefa_id>/', views.alterar_status_tarefa, name='alterar_status_tarefa'),
    path('alterar_prioridade_tarefa/<int:tarefa_id>/', views.alterar_prioridade_tarefa, name='alterar_prioridade_tarefa'),
    path('calendario/', views.calendario, name='calendario'),
    path('periodos/', views.lista_periodos, name='lista_periodos'),
    path('periodos/novo/', views.novo_periodo, name='novo_periodo'),
    path('materias/novo/', views.nova_materia, name='nova_materia'),
    path('tarefas/', views.lista_tarefas, name='lista_tarefas'),
    path('tarefas/novo/', views.nova_tarefa, name='nova_tarefa'),
    path('materiais/novo/', views.nova_materia, name='nova_materia'),
    
    #TinyMCE
    path('upload_image/', views.upload_image, name='upload_image'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    