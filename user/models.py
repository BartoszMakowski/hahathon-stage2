from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(User):
    class Meta:
        proxy = True

class Player(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    won = models.BooleanField(default=False)
    first = models.BooleanField()