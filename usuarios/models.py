from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    nome = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    data_entrada = models.DateTimeField(auto_now_add=True)
        
    email = models.EmailField(unique=True, blank=True, null=True)
    
    def __str__(self):
        return self.nome if self.nome else self.username
    
    def save(self, *args, **kwargs):
        if not self.nome and self.username:
            self.nome = self.username.capitalize()
            
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'