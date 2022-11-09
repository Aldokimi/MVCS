import lzma
import os, shutil, subprocess
import tarfile
import uuid
from django.http import Http404
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Repository, Commit, Branch
from .serializers import UserSerializer, CommitSerializer,\
     RepositorySerializer, BranchSerializer, RegistrationSerializer, PasswordChangeSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from .utils import get_tokens_for_user, get_repo_details
from rest_framework.parsers import JSONParser


# Authentication views
class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            path = os.path.join("/home/mvcs/", serializer.validated_data['username'] + '/')
            os.mkdir(path)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    parser_classes = [JSONParser]
    def post(self, request):
        if 'email' not in request.data or 'password' not in request.data:
            return Response({'msg': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)

        email = request.data.get('email', False)
        password = request.data.get('password', 'ERROR')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            auth_data = get_tokens_for_user(request.user)
            return Response(
                {'msg': 'Login Success', 'user_id': user.id, **auth_data}, status=status.HTTP_200_OK)
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
            self. renameDirectory('/home/mvcs/', user.username, serializer.validated_data['username'])
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        # Deleting the user and the directory belonging to the user
        user = self.get_object(pk)
        shutil.rmtree('/home/mvcs/' + user.username + '/')
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
            path = os.path.join(
                "/home/mvcs/" + repo.owner.username + '/', repositories.validated_data['name'])
            os.mkdir(path)
            
            ## Create a new branch called main which have a commit inside it
            # Create the main branch
            branch_request_data = {
                "repo": repo.id,
                "name": "main",
            }

            branch_data = BranchSerializer(data=branch_request_data)
            if branch_data.is_valid():
                branch_data.save()
                path_to_branch = os.path.join(
                    "/home/mvcs/" + repo.owner.username + '/' + repo.name, 
                    branch_data.validated_data['name'])
                os.mkdir(path_to_branch)
            else:
                os.rmdir(path)
                return Response(branch_data.errors, status=status.HTTP_400_BAD_REQUEST)

            try:
                branch = Branch.objects.get(
                    pk=branch_data.data['id'], name=branch_data.validated_data['name'])
            except Branch.DoesNotExist:
                raise Http404

            # Create the first commit in the main branch
            commit_request_data = {
                "message": 'Initial commit',
                "branch" : branch.id,
                "committer": repo.owner.id,
                "unique_id": uuid.uuid4().hex
            }

            commit_data = CommitSerializer(data=commit_request_data)
            if commit_data.is_valid():
                commit_data.save()
            else:
                os.rmdir(path)
                return Response(commit_data.errors, status=status.HTTP_400_BAD_REQUEST)

            # Create the compressed folder of the initial commit
            base_path = "/home/mvcs/" + repo.owner.username + '/' + repo.name + '/' + 'main'
            commit_unique_id = commit_data.validated_data['unique_id']
            commit_file_name = f'{commit_unique_id}.tar.xz'
            xz_file = lzma.LZMAFile(commit_file_name, mode='w')
            with tarfile.open(mode='w', fileobj=xz_file) as tar_xz_file:
                for file in os.listdir(base_path):
                    tar_xz_file.add(os.path.join(base_path, file))
            xz_file.close()
            shutil.copy2(commit_file_name, base_path)
            os.remove(commit_file_name)

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
            os.rename(
                '/home/mvcs/' + repository.owner.username + '/' + repository.name, 
                '/home/mvcs/' + repository.owner.username + '/' + serializer.validated_data['name']
            ) 
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        repository = self.get_object(pk)
        # Deleting the directory 
        shutil.rmtree('/home/mvcs/' + repository.owner.username + '/' + repository.name + '/')
        repository.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RepositoryDataDetail(APIView):
    """
    Get all the repository data.
    """
    def __get_user(self, name):
        try:
            return User.objects.get(username=name)
        except Repository.DoesNotExist:
            raise Http404
    
    def __get_object(self, name ,owner):
        try:
            return Repository.objects.get(owner=owner, name=name)
        except Repository.DoesNotExist:
            raise Http404
    
    def get(self, request, owner, name, format=None):
        owner_user = self.__get_user(owner)
        repo = self.__get_object(name, owner_user)
        print(repo.name, repo.id)
        data = get_repo_details(repo.id, owner_user.id)
        return Response(data)

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
            path = os.path.join(
                "/home/mvcs/" + repo.owner.username + '/' + repo.name, 
                branches.validated_data['name'])
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
            repo_dir = '/home/mvcs/' + branch.repo.owner.username + '/' + branch.repo.name + '/'
            os.rename( repo_dir + branch.name, repo_dir + serializer.validated_data['name']) 
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        branch = self.get_object(pk)
        # Deleting the directory 
        shutil.rmtree(
            '/home/mvcs/' + branch.repo.owner.username + '/' + branch.repo.name + '/' + branch.name + '/')
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
        base_path = "/home/mvcs/" + commit.branch.repo.owner.username\
             + '/' + commit.branch.repo.name + '/' + commit.branch.name
        os.remove(base_path + '/' + commit.unique_id + '.tar.xz')
        commit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
