import os
import json
import shutil
import tarfile

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

from ..models import Commit, Branch
from ..serializers import CreateCommitSerializer, UpdateCommitSerializer

from django.http import Http404


class CommitList(APIView):
    """
    List all commits, or create a new commit.
    """

    def get_branch_object(self, pk):
        try:
            return Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            raise Http404

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateCommitSerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return UpdateCommitSerializer

    def get(self, request, format=None):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        commits = Commit.objects.all()
        serializer = CreateCommitSerializer(commits, many=True)
        data = []

        for commit in serializer.data:
            branch_id = commit["branch"]
            branch = self.get_branch_object(branch_id)
            print(branch)
            repository = branch.repo
            if not repository.private:
                data.append(commit)
            else:
                if self.request.user.id == repository.owner or len(
                    [x for x in repository.contributors.all() if x.id ==
                     self.request.user.id]
                ) != 0:
                    data.append(commit)

        return Response(data)

    def post(self, request, format=None):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()

        serializer = self.get_serializer_class()
        commit = serializer(data=request.data)

        if commit.is_valid():
            try:
                branch = Branch.objects.get(pk=request.data["branch"])
            except:
                return Response(commit.errors, status=status.HTTP_400_BAD_REQUEST)

            if branch.repo.owner.id is not self.request.user.id and\
                    self.request.user.id not in [user.id for user in branch.repo.contributors.all()]:
                raise PermissionDenied()

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
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
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
                return Response({"Error": "You cannot modify those fields!"}, status=status.HTTP_400_BAD_REQUEST)

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
        try:
            os.remove(base_path + '/' + commit.unique_id + '.tar.xz')
        except:
            pass
        commit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommitTreeDetail(APIView):
    """
    Get teh file tree of a commit.
    """

    def get_object(self, pk):
        try:
            return Commit.objects.get(pk=pk)
        except Commit.DoesNotExist:
            raise Http404

    def path_to_dict(self, path):
        d = {'name': os.path.basename(path)}
        if os.path.isdir(path):
            d['type'] = "directory"
            d['children'] = [self.path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
        else:
            d['type'] = "file"
        return d

    def get(self, request, pk, format=None):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated()
        commit = self.get_object(pk)
        user_path = os.path.join("/home/mvcs/", f"{commit.branch.repo.owner.username}")
        repo_path = os.path.join(user_path, f"{commit.branch.repo.name}")
        branch_path = os.path.join(repo_path, f"{commit.branch.name}")
        commit_file = os.path.join(branch_path, f"{commit.unique_id}.tar.xz")
        working_dir = os.path.join(branch_path, "test")
        os.mkdir(working_dir)
        try:
            with tarfile.open(commit_file) as ccf:
                ccf.extractall(working_dir)
        except Exception as e:
            raise Exception(e)
        print(working_dir)
        data = self.path_to_dict(working_dir)
        shutil.rmtree(working_dir)
        data["name"] = commit.branch.repo.name
        return Response(data)