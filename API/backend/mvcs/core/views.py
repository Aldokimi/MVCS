import os, shutil, subprocess
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Repository, Commit, Branch
from .serializers import UserSerializer, CommitSerializer,\
     RepositorySerializer, BranchSerializer, RegistrationSerializer, PasswordChangeSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from .utils import get_tokens_for_user
from rest_framework.parsers import JSONParser


# Authentication views
class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            path = os.path.join("/var/mvcs/", serializer.validated_data['username'] + '/')
            os.mkdir(path)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    parser_classes = [JSONParser]
    def post(self, request):
        print(request.data)
        if 'email' not in request.data or 'password' not in request.data:
            return Response({'msg': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)

        email = request.data.get('email', False)
        password = request.data.get('password', 'ERROR')
        print(email, password)
        user = authenticate(request, email=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            auth_data = get_tokens_for_user(request.user)
            return Response({'msg': 'Login Success', **auth_data}, status=status.HTTP_200_OK)
        return Response({'msg': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'msg': 'Successfully Logged out'}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serializer = PasswordChangeSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True) 
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

# User views handling
class UserList(APIView):
    """
    List all users, or create a new user.
    """
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserDetail(APIView):
    """
    Retrieve, update or delete a user instance.
    """
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def renameDirectory(self, path, dir_name, new_name):
        subprocess.run(["mv", path + dir_name + '/', path + new_name+ '/'])

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            self. renameDirectory('/var/mvcs/', user.username, serializer.validated_data['username'])
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        # Deleting the user and the directory belonging to the user
        user = self.get_object(pk)
        shutil.rmtree('/var/mvcs/' + user.username + '/')
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Repository views handling
class RepositoryList(APIView):
    """
    List all repositories, or create a new repository.
    """
    def get_object(self, pk):
        try:
            return Repository.objects.get(pk=pk)
        except Repository.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        repositories = Repository.objects.all()
        serializer = RepositorySerializer(repositories, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        repositories = RepositorySerializer(data=request.data)
        if repositories.is_valid():
            repositories.save()
            # Create a new director for the repository under the user's directory
            repo = self.get_object(repositories.data['id'])
            path = os.path.join("/var/mvcs/" + repo.owner.username + '/', repositories.validated_data['name'])
            os.mkdir(path)
            return Response(repositories.data, status=status.HTTP_201_CREATED)
        return Response(repositories.errors, status=status.HTTP_400_BAD_REQUEST)

class RepositoryDetail(APIView):
    """
    Retrieve, update or delete a repository instance.
    """
    def get_object(self, pk):
        try:
            return Repository.objects.get(pk=pk)
        except Repository.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        repository = self.get_object(pk)
        serializer = RepositorySerializer(repository)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        repository = self.get_object(pk)
        serializer = RepositorySerializer(repository, data=request.data)
        if serializer.is_valid():
            # Rename the directory of the repository according to the update
            os.rename('/var/mvcs/' + repository.owner.username + '/' + repository.name, '/var/mvcs/' + repository.owner.username + '/' + serializer.validated_data['name']) 
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        repository = self.get_object(pk)
        # Deleting the directory 
        shutil.rmtree('/var/mvcs/' + repository.owner.username + '/' + repository.name + '/')
        repository.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Branch views handling
class BranchList(APIView):
    """
    List all branches, or create a new branch.
    """
    def get_object_by_parent(self, pk):
        try:
            return Branch.objects.filter(repo=pk)
        except Repository.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        branches = Branch.objects.all()
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        branches = BranchSerializer(data=request.data)
        if branches.is_valid():
            branches.save()
            # Create a new director for the repository under the user's directory
            repo = branches.validated_data['repo']
            path = os.path.join("/var/mvcs/" + repo.owner.username + '/' + repo.name, branches.validated_data['name'])
            os.mkdir(path)
            return Response(branches.data, status=status.HTTP_201_CREATED)
        return Response(branches.errors, status=status.HTTP_400_BAD_REQUEST)

class BranchDetail(APIView):
    """
    Retrieve, update or delete a branch instance.
    """
    def get_object(self, pk):
        try:
            return Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        branch = self.get_object(pk)
        serializer = BranchSerializer(branch)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        branch = self.get_object(pk)
        serializer = BranchSerializer(branch, data=request.data)
        if serializer.is_valid():
            # Rename the directory of the repository according to the update
            repo_dir = '/var/mvcs/' + branch.repo.owner.username + '/' + branch.repo.name + '/'
            os.rename( repo_dir + branch.name, repo_dir + serializer.validated_data['name']) 
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        branch = self.get_object(pk)
        # Deleting the directory 
        shutil.rmtree('/var/mvcs/' + branch.repo.owner.username + '/' + branch.repo.name + '/' + branch.name + '/')
        branch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Commit views handling
class CommitList(APIView):
    """
    List all commits, or create a new commit.
    """
    def get_object(self, pk):
        try:
            return Commit.objects.get(pk=pk)
        except Commit.DoesNotExist:
            raise Http404
    
    def get(self, request, format=None):
        commits = Commit.objects.all()
        serializer = CommitSerializer(commits, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        commits = CommitSerializer(data=request.data)
        if commits.is_valid():
            commits.save()
            branch = commits.validated_data['branch']
            base_path = "/var/mvcs/" + branch.repo.owner.username + '/' + branch.repo.name + '/' + branch.name
            path = os.path.join(base_path, commits.validated_data['unique_id'])
            os.mkdir(path)
            return Response(commits.data, status=status.HTTP_201_CREATED)
        return Response(commits.errors, status=status.HTTP_400_BAD_REQUEST)

class CommitDetail(APIView):
    """
    Retrieve, update or delete a commit instance.
    """
    def get_object(self, pk):
        try:
            return Commit.objects.get(pk=pk)
        except Commit.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        commit = self.get_object(pk)
        serializer = CommitSerializer(commit)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        commit = self.get_object(pk)
        serializer = CommitSerializer(commit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        commit = self.get_object(pk)
        base_path = "/var/mvcs/" + commit.branch.repo.owner.username + '/' + commit.branch.repo.name + '/' + commit.branch.name
        shutil.rmtree(base_path + '/' + commit.unique_id + '/')
        commit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)