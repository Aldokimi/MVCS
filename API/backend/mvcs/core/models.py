from datetime import datetime
from email import message
from operator import mod
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, AbstractUser

class User(AbstractUser):
    date_joined = models.DateTimeField(verbose_name="date joined", default=timezone.now, null=True)
    last_login  = models.DateTimeField(verbose_name="last login", default=timezone.now, null=True)
    first_name = models.CharField(max_length=60, null=True)
    last_name = models.CharField(max_length=60, null=True)
    bio = models.TextField(blank=True, null=True, max_length=2000)
    date_of_birth = models.DateTimeField(verbose_name="date of birth", null=True)
    profile_picture = models.ImageField(upload_to="image", blank=True, null=True)

    def __str__(self) -> str:
        return self.username + " " + self.email

    def has_perms(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class Repository(models.Model):
    name = models.CharField(max_length=500)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(verbose_name="date created", default=timezone.now)
    last_updated = models.DateTimeField(verbose_name="date joined", default=timezone.now)
    contributors = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='repo_contributors')
    private = models.BooleanField(default=False)

class Branch(models.Model):
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    date_created = models.DateTimeField(verbose_name="date created", default=timezone.now)
    has_locked_files = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)

class Commit(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    committer = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)
    message = models.TextField(max_length=1500)
    unique_id = models.CharField(max_length=64, unique=True)

