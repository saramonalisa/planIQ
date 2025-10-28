from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('inicio/', views.inicio, name='inicio'),

    # Registration
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('resetar-senha/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/resetar-senha/enviado/'
    ), name='password_reset'),
    path('resetar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('resetar-senha/confirmar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/resetar-senha/completo/'
    ), name='password_reset_confirm'),
    path('resetar-senha/completo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

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
    
    path('upload_image/', views.upload_image, name='upload_image'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
urlpatterns = [
    path('', views.home, name='home'),
    path('edit_profile/', views.editar_profile, name='edit_profile'),
]