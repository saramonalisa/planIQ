from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    data_entrada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
