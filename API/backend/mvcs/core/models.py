from datetime import datetime
from email import message
from operator import mod
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

class UserManager(BaseUserManager):
    def create_user(self, username, email, date_of_birth, password=None):
        """
        Creates and saves a User with the given username, email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        if not username:
            raise ValueError('User must have a username')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, date_of_birth, password=None):
        """
        Creates and saves a superuser with the given username, email, date of
        birth and password.
        """
        user = self.create_user(
            username,
            email,
            password=password,
            date_of_birth=date_of_birth,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=70, unique=True,)
    email = models.EmailField(max_length=255, unique=True,)
    date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    linkedin_token = models.TextField(blank=True, default='')
    date_joined = models.DateTimeField(verbose_name="date joined", default=timezone.now, null=True)
    last_login  = models.DateTimeField(verbose_name="last login", default=timezone.now, null=True)
    first_name = models.CharField(max_length=60, null=True)
    last_name = models.CharField(max_length=60, null=True)
    bio = models.TextField(blank=True, null=True, max_length=2000)
    date_of_birth = models.DateTimeField(verbose_name="date of birth", null=True)
    profile_picture = models.ImageField(upload_to="image", blank=True, null=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def linkedin_signed_in(self):

        return bool(self.linkedin_token) and self.expiry_date > timezone.now()

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

