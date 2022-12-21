import os
import shutil

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

from ..models import Repository, Commit, Branch
from ..serializers import CreateBranchSerializer, UpdateBranchSerializer
from ..utils import get_repo_branches

from django.http import Http404


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

