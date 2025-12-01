from django.db import models
from django.contrib.auth.models import AbstractBaseUser, User

class EmailVerificationOtp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254)
    otp = models.PositiveIntegerField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user
    
class User(AbstractBaseUser):
    pass

class LoginOtp(models.Model):
    email = models.EmailField(max_length=254, unique=True)
    otp = models.PositiveIntegerField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
    
    class Meta:
        db_table = "login_otp"
        ordering = ["-updated"]
