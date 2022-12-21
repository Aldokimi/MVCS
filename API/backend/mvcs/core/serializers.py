from rest_framework import serializers
from .models import User, Repository, Branch, Commit


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = User(
            username=self.validated_data['username'], email=self.validated_data['email'])
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError(
                {'password': 'Passwords must match.'})
        user.set_password(password)
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        style={"input_type": "password"}, required=True)
    new_password = serializers.CharField(
        style={"input_type": "password"}, required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(
                {'current_password': 'Does not match'})
        return value


class OwnUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'email', 'is_active', 
            'is_admin', 'linkedin_token', 'date_joined',
            'last_login', 'first_name', 'last_name', 'bio', 
            'date_of_birth', 'profile_picture', 'public_key',
        ]


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'is_active', 'date_joined',
            'first_name', 'last_name', 'bio', 'date_of_birth', 'profile_picture',
        ]


class UpdateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100, required=False)
    email = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'linkedin_token', 'first_name',
            'last_name', 'bio', 'date_of_birth', 'profile_picture', 'public_key',
        ]


class CreateRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ['id', 'name', 'date_created', 'last_updated', 'private',
                  'contributors', 'owner', 'clone_url', 'description', ]


class UpdateRepositorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = Repository
        fields = ['name', 'private', 'contributors', 'description', ]


class CreateBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'date_created',
                  'has_locked_files', 'locked_files', 'repo',]


class UpdateBranchSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = Branch
        fields = ['id', 'name', 'has_locked_files', 'locked_files',]


class CreateCommitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commit
        fields = ['id', 'date_created', 'date_updated',
                  'message', 'branch', 'committer', 'unique_id',]


class UpdateCommitSerializer(serializers.ModelSerializer):
    message = serializers.CharField(max_length=700, required=False)

    class Meta:
        model = Commit
        fields = ['id', 'message',]
