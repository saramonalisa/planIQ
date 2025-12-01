from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings 

urlpatterns = [
    path('', include("app.urls", namespace='app')),
    path('accounts/', include('allauth.urls')),
    path('usuarios/', include("usuarios.urls", namespace='usuarios')),
    path('tinymce/', include('tinymce.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
