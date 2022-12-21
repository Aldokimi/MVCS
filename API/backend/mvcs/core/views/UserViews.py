import shutil
import subprocess

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

from ..models import User
from ..serializers import CreateUserSerializer, UpdateUserSerializer
from ..utils import get_user_branches, get_user_repositories, get_user_commits

from django.http import Http404

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
            print(request.data)

            if "username" in request.data:
                if user.username != serializer.validated_data["username"]:
                    self.renameDirectory(
                        '/home/mvcs/',
                        user.username,
                        serializer.validated_data['username']
                    )
            if "public_key" in request.data:
                print(request.data["public_key"])
                # Add this public key to the end of the authorized_keys file
                try:
                    with open("/home/mvcs/.ssh/authorized_keys", "a") as myfile:
                        print(myfile)
                        myfile.write(
                            "\n" + serializer.validated_data['public_key'])
                except:
                    print("couldn't upload ssh key")

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
