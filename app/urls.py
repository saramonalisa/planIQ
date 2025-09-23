from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('inicio/', views.inicio, name='inicio'),
    path('nova_tarefa/', views.nova_tarefa, name='nova_tarefa'),
    path('editar_tarefa/', views.editar_tarefa, name='editar_tarefa'),
    path('detalhar_tarefa/<int:tarefa_id>/', views.detalhar_tarefa, name='detalhar_tarefa'),
    path('editar_tarefa/<int:tarefa_id>/', views.editar_tarefa, name='editar_tarefa'),
    path('excluir_tarefa/<int:tarefa_id>/', views.excluir_tarefa, name='excluir_tarefa'),
    path('marcar_concluida/<int:tarefa_id>/', views.marcar_concluida, name='marcar_concluida'),
    ]
