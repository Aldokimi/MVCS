from email import message
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Repository(models.Model):
    name  = models.CharField(max_length=500)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # contributors = models.ManyToManyField(User)
    def __str__(self) -> str:
        return self.name + ' ' + self.owner


class Branch(models.Model):
    name = models.CharField(max_length=500)
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name + ' ' + self.repo

class Commit(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    committer = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    date_created = models.TimeField(default=timezone.now)
    message = models.TextField()

    def __str__(self) -> str:
        return self.branch + ' \n' + self.committer + ' \n' + self.date_created + ' \n' + self.message
