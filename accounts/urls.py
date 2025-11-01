from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

app_name='accounts'

urlpatterns = [
    # Registration
    path('cadastro/', views.cadastro, name='cadastro'),
    path('configuracoes/', views.editar_perfil, name='configuracoes'),
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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)