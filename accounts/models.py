from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    rut = models.CharField(max_length=16)
    phone = models.CharField(max_length=12)
    email = models.EmailField()
    password = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_mod = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
