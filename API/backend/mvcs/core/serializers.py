from rest_framework import serializers
from .models import Repository, Branch, Commit, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=[
                'id',
                'password',
                'is_superuser',
                'username',
                'is_staff',
                'is_active',
                'email',
                'date_joined',
                'last_login',
                'first_name',
                'last_name',
                'bio',
                'date_of_birth',
                'profile_picture',
                'groups',
                'user_permissions',
            ]
class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields=[
                'id',
                'name',
                'date_created',
                'last_updated',
                'private',
                'contributors',
                'owner',
            ]

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields=[
                'repo',
                'id',
                'name',
                'date_created',
                'has_locked_files',
                'locked',
            ]

class CommitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commit
        fields=[
                'id',
                'date_created',
                'date_updated',
                'message',
                'branch',
                'committer',
                'unique_id',
            ]