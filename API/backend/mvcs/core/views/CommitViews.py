import os

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
