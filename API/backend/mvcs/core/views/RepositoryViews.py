import lzma
import os
import shutil
import tarfile
import uuid
from netifaces import AF_INET
import netifaces as ni

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

from ..models import User, Repository, Branch
from ..serializers import CreateRepositorySerializer, UpdateRepositorySerializer,\
    CreateBranchSerializer, CreateCommitSerializer
from ..utils import get_repo_details

from django.http import Http404


class RepositoryList(APIView):
    """
    List all repositories, or create a new repository.
    """

    def get_object(self, pk):
        try:
            return Repository.objects.get(pk=pk)
        except Repository.DoesNotExist:
            raise Http404

    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get_clone_url(self, username, repo_name):
        ip = ni.ifaddresses('eth0')[AF_INET][0]['addr']
        return f'mvcs@{ip}:~/{username}/{repo_name}'

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateRepositorySerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return UpdateRepositorySerializer

    def get(self, request, format=None):
        repositories = Repository.objects.all()
        serializer = CreateRepositorySerializer(repositories, many=True)
        data = []

        for repository in serializer.data:
            if not repository["private"]:
                data.append(repository)
            else:
                if self.request.user.id == repository["owner"] or len(
                    [x for x in repository["contributors"] if x ==
                     self.request.user.id]
                ) != 0:
                    data.append(repository)

        return Response(data)

    def post(self, request, format=None):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()

        serializer = self.get_serializer_class()
        repositories = serializer(data=request.data)

        if repositories.is_valid():
            repository = repositories.validated_data
            print(self.request.user.id, repository["owner"].id)
            if self.request.user.id != repository["owner"].id:
                raise PermissionDenied()

            # get the clone URL
            username = self.get_user(request.data["owner"]).username
            request.data["clone_url"] = self.get_clone_url(
                username, request.data["name"])
            repositories.save()
            # Create a new director for the repository under the user's directory
            repo = self.get_object(repositories.data['id'])
            path = os.path.join(
                "/home/mvcs/" + repo.owner.username + '/', repositories.validated_data['name'])
            try:
                os.mkdir(path)
                os.system(f"chown -R mvcs:mvcs {path}")
            except:
                pass

            # Create a new branch called main which have a commit inside it
            # Create the main branch
            branch_request_data = {
                "repo": repo.id,
                "name": "main",
            }

            branch_data = CreateBranchSerializer(data=branch_request_data)
            if branch_data.is_valid():
                branch_data.save()
                path_to_branch = os.path.join(
                    "/home/mvcs/" + repo.owner.username + '/' + repo.name,
                    branch_data.validated_data['name'])
                try:
                    os.mkdir(path_to_branch)
                    os.system(f"chown -R mvcs:mvcs {path_to_branch}")
                except:
                    pass
            else:
                try:
                    os.rmdir(path)
                    os.system(f"chown -R mvcs:mvcs {path}")
                except:
                    pass
                return Response(branch_data.errors, status=status.HTTP_400_BAD_REQUEST)

            try:
                branch = Branch.objects.get(
                    pk=branch_data.data['id'], name=branch_data.validated_data['name'])
            except Branch.DoesNotExist:
                raise Http404

            # Create the first commit in the main branch
            commit_request_data = {
                "message": 'Initial commit',
                "branch": branch.id,
                "committer": repo.owner.id,
                "unique_id": uuid.uuid4().hex
            }

            commit_data = CreateCommitSerializer(data=commit_request_data)
            if commit_data.is_valid():
                commit_data.save()
            else:
                try:
                    os.rmdir(path)
                except:
                    pass
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
            try:
                shutil.copy2(commit_file_name, base_path)
                os.system(
                    f"chown -R mvcs:mvcs {os.path.join(base_path, commit_file_name)}")
                os.remove(commit_file_name)
            except:
                pass

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

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateRepositorySerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return UpdateRepositorySerializer

    def get(self, request, pk, format=None):
        repository = self.get_object(pk)
        if repository.private and not (
            self.request.user.id == repository.owner.id or len(
                [x for x in repository.contributors.all() if x.id == self.request.user.id]) != 0
        ):
            raise PermissionDenied()
        serializer = CreateRepositorySerializer(repository)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        repository = self.get_object(pk)
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()

        if repository.owner.id is not self.request.user.id:
            if len([x for x in repository.contributors.all() if x.id == self.request.user.id]) == 0:
                raise PermissionDenied()

        if repository.private and not (self.request.user.id == repository.owner.id or len(
                [x for x in repository.contributors.all() if x.id == self.request.user.id]) != 0):
            raise PermissionDenied()

        notAllowedValues = ["id", "date_created", "owner"]
        for k in request.data:
            if k in notAllowedValues:
                return Response(
                    {"Error": "You cannot modify this field!"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        ser = self.get_serializer_class()
        serializer = ser(repository, data=request.data)
        if serializer.is_valid():
            # Rename the directory of the repository according to the update
            try:
                if request.data["name"]:
                    os.rename(
                        '/home/mvcs/' + repository.owner.username + '/' + repository.name,
                        '/home/mvcs/' + repository.owner.username +
                        '/' + serializer.validated_data['name']
                    )
            except:
                pass
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        repository = self.get_object(pk)
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        if repository.owner.id is not self.request.user.id:
            raise PermissionDenied()
        # Deleting the directory
        try:
            shutil.rmtree('/home/mvcs/' + repository.owner.username +
                          '/' + repository.name + '/')
        except:
            pass
        repository.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RepositoryDataDetail(APIView):
    """Get all data from the repository, this data contains the repository owner data,
    every branch inside the repository with its data, and every commit inside every branch
    with its data. 

    This can be used as a configuration data for the CLI application.
    """

    def __get_user(self, name):
        try:
            return User.objects.get(username=name)
        except Repository.DoesNotExist:
            raise Http404

    def __get_object(self, name, owner):
        try:
            return Repository.objects.get(owner=owner, name=name)
        except Repository.DoesNotExist:
            raise Http404

    def get(self, request, owner, name, format=None):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        owner_user = self.__get_user(owner)
        repo = self.__get_object(name, owner_user)
        if (repo.owner.id is not self.request.user.id):
            if len(
                    [x for x in repo.contributors.all() if x.id == self.request.user.id]) == 0:
                raise PermissionDenied()

        if repo.private and not (self.request.user.id == repo.owner.id or len(
                [x for x in repo.contributors.all() if x.id == self.request.user.id]) != 0):
            raise PermissionDenied()
        data = get_repo_details(repo.id, owner_user.id)
        return Response(data)
