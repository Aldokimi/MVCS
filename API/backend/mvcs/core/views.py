import lzma
import os
import shutil
import subprocess
import tarfile
import uuid
from netifaces import AF_INET
import netifaces as ni

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

from .models import User, Repository, Commit, Branch
from .serializers import CreateUserSerializer, UpdateUserSerializer,\
    CreateRepositorySerializer, UpdateRepositorySerializer,\
    RegistrationSerializer, PasswordChangeSerializer,\
    CreateBranchSerializer, UpdateBranchSerializer,\
    CreateCommitSerializer, UpdateCommitSerializer
from .utils import get_tokens_for_user, get_repo_details,\
    get_user_branches, get_repo_branches, get_user_repositories, get_user_commits

from django.http import Http404
from django.contrib.auth import authenticate, login, logout


"""
# Authentication views
"""


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            path = os.path.join(
                "/home/mvcs/", serializer.validated_data['username'] + '/')
            os.mkdir(path)
            os.system(f"chown -R mvcs:mvcs {path}")
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
        serializer = PasswordChangeSerializer(
            context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


"""
# User views handling
"""


class UserList(APIView):
    """
    List all users, or create a new user.
    """

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = CreateUserSerializer(users, many=True)
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
        subprocess.run(["mv", path + dir_name + '/', path + new_name + '/'])

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateUserSerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return UpdateUserSerializer

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        serializer = CreateUserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        # Set permissions
        user = self.get_object(pk)
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        if user.id is not self.request.user.id:
            raise PermissionDenied()

        notAllowedValues = ["is_active", "id", "is_admin", "date_joined"]
        for k in request.data:
            if k in notAllowedValues:
                return Response({"Error": "You cannot modify this field!"}, status=status.HTTP_400_BAD_REQUEST)

        get_ser = self.get_serializer_class()
        serializer = get_ser(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            try:
                if request.data["email"]:
                    if user.email != serializer.validated_data["email"]:
                        self.renameDirectory(
                            '/home/mvcs/',
                            user.username,
                            serializer.validated_data['username']
                        )
                if request.data["public_key"]:
                    # Add this public key to the end of the authorized_keys file
                    with open("/home/mvcs/.ssh/authorized_keys", "a") as myfile:
                        myfile.write(
                            "\n" + serializer.validated_data['test.txt'])
            except:
                pass
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        # Deleting the user and the directory belonging to the user
        user = self.get_object(pk)
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        if user.id is not self.request.user.id:
            raise PermissionDenied()

        shutil.rmtree('/home/mvcs/' + user.username + '/')
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRepositories(APIView):
    """
    Get all the repositories for a user.
    """

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        user = self.get_object(pk)
        data = get_user_repositories(user.id)
        return Response(data)


class UserBranches(APIView):
    """
    Get all the branches for a user.
    """

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        user = self.get_object(pk)
        data = get_user_branches(user.id)
        return Response(data)


class UserCommits(APIView):
    """
    Get all the branches for a user.
    """

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        user = self.get_object(pk)
        data = get_user_commits(user.id)
        return Response(data)



"""
# Repository views handling
"""


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
        return Response(serializer.data)

    def post(self, request, format=None):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        serializer = self.get_serializer_class()
        # get the clone URL
        username = self.get_user(request.data["owner"]).username
        print(username, request.data["name"])
        request.data["clone_url"] = self.get_clone_url(
            username, request.data["name"])

        repositories = serializer(data=request.data)
        if repositories.is_valid():
            repositories.save()
            # Create a new director for the repository under the user's directory
            repo = self.get_object(repositories.data['id'])
            path = os.path.join(
                "/home/mvcs/" + repo.owner.username + '/', repositories.validated_data['name'])
            os.mkdir(path)
            os.system(f"chown -R mvcs:mvcs {path}")

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
                os.mkdir(path_to_branch)
                os.system(f"chown -R mvcs:mvcs {path_to_branch}")
            else:
                os.rmdir(path)
                os.system(f"chown -R mvcs:mvcs {path}")
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
            os.system(
                f"chown -R mvcs:mvcs {os.path.join(base_path, commit_file_name)}")
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

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateRepositorySerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return UpdateRepositorySerializer

    def get(self, request, pk, format=None):
        repository = self.get_object(pk)
        serializer = CreateRepositorySerializer(repository)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        repository = self.get_object(pk)
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        if repository.owner.id is not self.request.user.id:
            raise PermissionDenied()

        notAllowedValues = ["id", "date_created", "owner"]
        for k in request.data:
            if k in notAllowedValues:
                return Response({"Error": "You cannot modify this field!"}, status=status.HTTP_400_BAD_REQUEST)

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
        shutil.rmtree('/home/mvcs/' + repository.owner.username +
                      '/' + repository.name + '/')
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
        print(owner_user, repo)
        print(repo.name, repo.id)
        data = get_repo_details(repo.id, owner_user.id)
        return Response(data)


"""
# Branch views handling
"""


class BranchList(APIView):
    """
    List all branches, or create a new branch.
    """

    def get_branch_object(self, pk):
        try:
            return Branch.objects.filter(repo=pk)
        except Repository.DoesNotExist:
            raise Http404

    def get_repo_object(self, pk):
        try:
            return Repository.objects.filter(repo=pk)
        except Repository.DoesNotExist:
            raise Http404

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateBranchSerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return UpdateBranchSerializer

    def get(self, request, format=None):
        branches = Branch.objects.all()
        serializer = CreateBranchSerializer(branches, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = self.get_serializer_class()
        branch = serializer(data=request.data)
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()

        # if request.data['repo'] and self.get_repo_object(request.data['repo']).owner.id is not self.request.user.id and\
        #     self.request.user.id not in [user.id for user in self.get_repo_object(request.data['repo']).contributors.all()]:
        #     raise PermissionDenied()

        if branch.is_valid():
            # Check if we have a branch with the same name in the belonging repository
            for x in get_repo_branches(branch.validated_data["repo"]):
                if x.name == branch.validated_data["name"]:
                    return Response(
                        {'Error': 'This branch already exists!'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            branch.save()
            # Create a new director for the repository under the user's directory
            repo = branch.validated_data['repo']
            path = os.path.join(
                "/home/mvcs/" + repo.owner.username + '/' + repo.name,
                branch.validated_data['name'])
            os.mkdir(path)
            os.system(f"chown -R mvcs:mvcs {path}")

            # Get the main branch of the repo
            branches = Branch.objects.filter(
                repo=branch.data['repo'], name="main")
            main_branch = branches.first()
            print(main_branch.name)
            last_commit = self.get_last_commit(main_branch.id)

            # Copy the last commit from the main branch
            base_path = "/home/mvcs/" +\
                repo.owner.username + '/' + repo.name + \
                '/' + branch.validated_data['name']
            main_branch_dir = "/home/mvcs/" +\
                repo.owner.username + '/' + repo.name + '/' + "main"
            commit_file_name = f'{last_commit.unique_id}.tar.xz'

            shutil.copy(os.path.join(main_branch_dir,
                        commit_file_name), base_path)
            os.system(
                f"chown -R mvcs:mvcs {os.path.join(base_path, commit_file_name)}")

            return Response(branch.data, status=status.HTTP_201_CREATED)
        return Response(branch.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_last_commit(self, branch_id):
        commits = Commit.objects.filter(branch=branch_id)
        latest_commit = commits.first()
        for commit in commits:
            if commit.date_created > latest_commit.date_created:
                latest_commit = commit
        return latest_commit


class BranchDetail(APIView):
    """
    Retrieve, update or delete a branch instance.
    """

    def get_object(self, pk):
        try:
            return Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            raise Http404

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateBranchSerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return UpdateBranchSerializer

    def get(self, request, pk, format=None):
        branch = self.get_object(pk)
        serializer = CreateBranchSerializer(branch)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        branch = self.get_object(pk)
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        if branch.repo.owner.id is not self.request.user.id:
            raise PermissionDenied()
        if branch.name == "main":
            return Response(
                {'Error': 'You cannot modify the main branch!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        notAllowedValues = ["date_created", "id", "repo"]
        for k in request.data:
            if k in notAllowedValues:
                return Response({"Error": "You cannot modify this field!"}, status=status.HTTP_400_BAD_REQUEST)

        ser = self.get_serializer_class()
        serializer = ser(branch, data=request.data)
        if serializer.is_valid():
            # Rename the directory of the repository according to the update
            try:
                if request.data["name"]:
                    repo_dir = '/home/mvcs/' + branch.repo.owner.username + '/' + branch.repo.name + '/'
                    os.rename(repo_dir + branch.name, repo_dir +
                              serializer.validated_data['name'])
            except:
                pass
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        branch = self.get_object(pk)
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        if branch.repo.owner.id is not self.request.user.id:
            raise PermissionDenied()
        if branch.name == "main":
            return Response(
                {'Error': 'You cannot delete the main branch!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Deleting the directory
        shutil.rmtree(
            '/home/mvcs/' + branch.repo.owner.username +
            '/' + branch.repo.name + '/' + branch.name + '/')
        branch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


"""
# Commit views handling
"""


class CommitList(APIView):
    """
    List all commits, or create a new commit.
    """

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateCommitSerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return UpdateCommitSerializer

    def get(self, request, format=None):
        commits = Commit.objects.all()
        serializer = CreateCommitSerializer(commits, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()

        serializer = self.get_serializer_class()
        commit = serializer(data=request.data)

        try:
            branch = Branch.objects.get(pk=request.data["branch"])
        except:
            return Response(commit.errors, status=status.HTTP_400_BAD_REQUEST)

        print(self.request.user.id, [
              user.id for user in branch.repo.contributors.all()])
        if branch.repo.owner.id is not self.request.user.id and\
                self.request.user.id not in [user.id for user in branch.repo.contributors.all()]:
            raise PermissionDenied()

        if commit.is_valid():
            commit.save()
            return Response(commit.data, status=status.HTTP_201_CREATED)
        return Response(commit.errors, status=status.HTTP_400_BAD_REQUEST)


class CommitDetail(APIView):
    """
    Retrieve, update or delete a commit instance.
    """

    def get_object(self, pk):
        try:
            return Commit.objects.get(pk=pk)
        except Commit.DoesNotExist:
            raise Http404

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateCommitSerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return UpdateCommitSerializer

    def get(self, request, pk, format=None):
        commit = self.get_object(pk)
        serializer = CreateCommitSerializer(commit)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        commit = self.get_object(pk)
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        if commit.branch.repo.owner.id is not self.request.user.id and\
                self.request.user.id not in [user.id for user in commit.branch.repo.contributors.all()]:
            raise PermissionDenied()

        notAllowedValues = ["date_created", "id",
                            "branch", "unique_id", "committer"]
        for k in request.data:
            if k in notAllowedValues:
                return Response({"Error": "You cannot modify this field!"}, status=status.HTTP_400_BAD_REQUEST)

        ser = self.get_serializer_class()
        serializer = ser(commit, data=request.data)
        if serializer.is_valid():
            serializer.validated_data["committer"] = self.request.user
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        commit = self.get_object(pk)
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        if commit.branch.repo.owner.id is not self.request.user.id:
            raise PermissionDenied()
        base_path = "/home/mvcs/" + commit.branch.repo.owner.username\
            + '/' + commit.branch.repo.name + '/' + commit.branch.name
        os.remove(base_path + '/' + commit.unique_id + '.tar.xz')
        commit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
