from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Repository, Branch, Commit, User

admin.site.register(Repository)
admin.site.register(Branch)
admin.site.register(Commit)
admin.site.register(User, UserAdmin)
