from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    
    #Tarefas
    path('tarefas/novo/', views.nova_tarefa, name='nova_tarefa'),
    path('tarefas/detalhar/<int:tarefa_id>/', views.detalhar_tarefa, name='detalhar_tarefa'),
    path('minhas_tarefas/', views.minhas_tarefas, name='minhas_tarefas'),
    path('tarefas/<int:ano>/<int:mes>/<int:dia>/', views.tarefas_do_dia, name='tarefas_do_dia'),
    path('tarefas/editar/<int:tarefa_id>/', views.editar_tarefa, name='editar_tarefa'),
    path('tarefas/excluir/<int:tarefa_id>/', views.excluir_tarefa, name='excluir_tarefa'),
    path('tarefas/alterar_status/<int:tarefa_id>/', views.alterar_status_tarefa, name='alterar_status_tarefa'),
    path('tarefas/alterar_prioridade/<int:tarefa_id>/', views.alterar_prioridade_tarefa, name='alterar_prioridade_tarefa'),
    path('calendario/', views.calendario, name='calendario'),
    
    #Acadêmico
    path('periodos/', views.lista_periodos, name='lista_periodos'),
    path('periodos/novo/', views.novo_periodo, name='novo_periodo'),
    path('materias/novo/', views.nova_materia, name='nova_materia'),
    path('materiais/novo/', views.nova_materia, name='nova_materia'),
    
    #TinyMCE
    path('upload_image/', views.upload_image, name='upload_image'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    