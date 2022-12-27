import shutil

from core.models import User, Repository, Branch, Commit
from core.views.AuthViews import RegistrationView, LoginView, ChangePasswordView
from core.views.UserViews import UserDetail
from core.views.RepositoryViews import RepositoryDetail, RepositoryList
from core.views.BranchViews import BranchDetail, BranchList
from core.views.CommitViews import CommitDetail, CommitList

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.renderers import JSONRenderer
from rest_framework.test import force_authenticate

from rest_framework.authtoken.models import Token
from django.contrib.sessions.middleware import SessionMiddleware


class test_case_user_registration(APITestCase):

    @classmethod
    def setUpTestData(self):
        self.url = 'http://127.0.0.1:8000/api/v1/register/'

        self.valid_payload = {
            "username": "test_case_user_registration",
            "email": "test_case_user_registration@email.com",
            "password": "passwordXD",
            "password2": "passwordXD"
        }

        # Test data
        self.existing_user_payload = {
            "username": "test_case_user_registration",
            "email": "test_case_user_registration@email.com",
            "password": "defaultpassword",
            "password2": "defaultpassword"
        }

        self.invalid_email_payload = {
            "username": "test_case_user_registration_invalid",
            "email": "test_case_user_registration_invalid.email.com",
            "password": "passwordXD",
            "password2": "passwordXD"
        }

        self.invalid_password_payload = {
            "username": "test_case_user_registration",
            "email": "test_case_user_registration@email.com",
            "password": "passwordXD",
            "password2": "passwow"
        }

        self.empty_email = {
            "username": "empty",
            "email": "",
            "password": "passwordXD",
            "password2": "passwow"
        }

        self.empty_password = {
            "username": "empty",
            "email": "empty@email.com",
            "password": "",
            "password2": "passwow"
        }

    @classmethod
    def tearDownClass(self):
        file_to_delete = "/home/mvcs/test_case_user_registration"
        try:
            shutil.rmtree(file_to_delete)
        except:
            print(f"Couldn't delete the file {file_to_delete}!")

    def Perform_Test(self, data):
        factory = APIRequestFactory()
        request = factory.post(self.url, data, format='json')
        user_view = RegistrationView.as_view()
        response = user_view(request)
        return response

    def test_register_new_user(self):
        response = self.Perform_Test(self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.Perform_Test(self.existing_user_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_invalid_email(self):
        response = self.Perform_Test(self.invalid_email_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_invalid_password(self):
        response = self.Perform_Test(self.invalid_password_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_email_or_password(self):
        response = self.Perform_Test(self.empty_email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.Perform_Test(self.empty_password)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class test_case_user_login(APITestCase):

    @classmethod
    def setUpTestData(self):
        self.url = 'http://127.0.0.1:8000/api/v1/login/'

        # Create a new user
        new_user_data = {
            "username": "test_case_user_login",
            "email": "test_case_user_login@email.com",
            "password": "password77",
            "password2": "password77"
        }

        factory = APIRequestFactory()
        request = factory.post(
            'http://127.0.0.1:8000/api/v1/register/',
            new_user_data, format='json')
        user_view = RegistrationView.as_view()
        response = user_view(request)

        if response.status_code == status.HTTP_201_CREATED:
            self.user = User.objects.filter(
                email="test_case_user_login@email.com").first()
            self.token = Token.objects.create(user=self.user)
            self.token.save()
        else:
            raise Exception("Error occurred during creating a test user!")

        # Test data
        self.valid_payload = {
            "email": self.user.email,
            "password": "password77"
        }

        self.invalid_email_payload = {
            "email": "test_user_creation.email.com",
            "password": "defaultpassword"
        }

        self.none_existing_user_payload = {
            "email": "idontexistemail@email.com",
            "password": "defaultpassword"
        }

        self.invalid_password_payload = {
            "email": self.user.email,
            "password": "passwordINVALID"
        }

    @classmethod
    def tearDownClass(self):
        file_to_delete = "/home/mvcs/test_case_user_login"
        try:
            shutil.rmtree(file_to_delete)
        except:
            print(f"Couldn't delete the file {file_to_delete}!")

    def Perform_Test(self, data, user=None):

        request_factory = APIRequestFactory()
        view = LoginView.as_view()

        request = request_factory.post(
            self.url, data, format="json",
            HTTP_AUTHORIZATION='Token {}'.format(self.token))
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        force_authenticate(request, user)

        # Response obtained from request returned from view
        response = view(request)
        return response

    def test_login_user(self):
        response = self.Perform_Test(self.valid_payload, self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_none_existing_user(self):
        response = self.Perform_Test(self.none_existing_user_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_user_with_invalid_email(self):
        response = self.Perform_Test(self.invalid_email_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_user_with_invalid_password(self):
        response = self.Perform_Test(self.invalid_password_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class test_case_user_delete(APITestCase):

    @classmethod
    def setUpTestData(self):

        u1 = {
            "username": "test1",
            "email": "test_user1@email.com",
            "password": "bruhLOGIN1",
            "password2": "bruhLOGIN1"
        }
        u2 = {
            "username": "test2",
            "email": "test_user2@email.com",
            "password": "bruhLOGIN2",
            "password2": "bruhLOGIN2"
        }

        factory = APIRequestFactory()
        request1 = factory.post(
            'http://127.0.0.1:8000/api/v1/register/', u1, format='json')
        request2 = factory.post(
            'http://127.0.0.1:8000/api/v1/register/', u2, format='json')
        user_view1 = RegistrationView.as_view()
        user_view2 = RegistrationView.as_view()
        response1 = user_view1(request1)
        response2 = user_view2(request2)

        if response1.status_code == status.HTTP_201_CREATED and\
                response2.status_code == status.HTTP_201_CREATED:
            pass
        else:
            raise Exception("Error occurred during creating a test user!")

        self.user1_payload = {
            "email": "test_user1@email.com",
            "password": "bruhLOGIN1"
        }
        self.user2_payload = {
            "email": "test_user2@email.com",
            "password": "bruhLOGIN2"
        }
        self.user_invalid = {
            "email": "iam_invalid@email.com",
            "password": "iam_invalid"
        }

    @classmethod
    def tearDownClass(self):
        file_to_delete = "/home/mvcs/test1"
        try:
            shutil.rmtree(file_to_delete)
        except:
            print(f"Couldn't delete the file {file_to_delete}!")

        file_to_delete = "/home/mvcs/test2"
        try:
            shutil.rmtree(file_to_delete)
        except:
            print(f"Couldn't delete the file {file_to_delete}!")

    def Perform_Test(self, user1, user2=None):

        # Logging into the user
        factory_login = APIRequestFactory()
        user_view_login = LoginView.as_view()

        request_login = factory_login.post(
            'http://127.0.0.1:8000/api/v1/login/', user1, format='json')
        middleware = SessionMiddleware()
        middleware.process_request(request_login)
        request_login.session.save()
        force_authenticate(request_login, user1)
        response_login = user_view_login(request_login)

        if not response_login.status_code == status.HTTP_200_OK:
            raise Exception(
                "Error occurred during login to test user!")

        factory_official = APIRequestFactory()
        user_view_official = UserDetail.as_view()
        theURL = "http://127.0.0.1:8000/api/v1/users/"

        # User1 wants to delete user2
        if (user2):

            x = User.objects.filter(email=user2['email']).first()
            request_official = factory_official.delete(
                f"{theURL}{x.id}", user2, format='json',
                HTTP_AUTHORIZATION=f"Bearer {response_login.data['access']}"
            )
            response_official = user_view_official(request_official, pk=x.id)
        # User1 wants to delete themselves
        else:
            x = User.objects.filter(email=user1['email']).first()
            request_official = factory_official.delete(
                f"{theURL}{x.id}", user1, format='json',
                HTTP_AUTHORIZATION=f"Bearer {response_login.data['access']}"
            )
            response_official = user_view_official(request_official, pk=x.id)
        return response_official

    def test_delete_user_owner(self):
        response = self.Perform_Test(self.user1_payload)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_user_notowner(self):
        response = self.Perform_Test(self.user1_payload, self.user2_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class test_case_user_changepassword(APITestCase):

    @classmethod
    def setUpTestData(self):

        user_change_password = {
            "username": "user_change_password",
            "email": "user_change_password@email.com",
            "password": "bruhChangePassword",
            "password2": "bruhChangePassword"
        }

        self.user_payload_changePass = {
            "email": "user_change_password@email.com",
            "current_password": "bruhChangePassword",
            "new_password": "bruhChangePasswordNEW"
        }

        self.user_payload_toLoginNewPass = {
            "email": "user_change_password@email.com",
            "password": "bruhChangePasswordNEW"
        }
        self.user_payload_toLoginOldPass = {
            "email": "user_change_password@email.com",
            "password": "bruhChangePassword"
        }

        factory = APIRequestFactory()
        request = factory.post(
            'http://127.0.0.1:8000/api/v1/register/', 
            user_change_password, format='json'
        )
        user_view = RegistrationView.as_view()
        response = user_view(request)

        if response.status_code == status.HTTP_201_CREATED:
            pass
        else:
            raise Exception("Error occurred during creating a test user!")

    @classmethod
    def tearDownClass(self):
        file_to_delete = "/home/mvcs/user_change_password"
        try:
            shutil.rmtree(file_to_delete)
        except:
            print(f"Couldn't delete the file {file_to_delete}!")

    def Perform_Login(self, dataLogin):

        # Logging into the user
        factory_login = APIRequestFactory()
        user_view_login = LoginView.as_view()

        request_login = factory_login.post(
            'http://127.0.0.1:8000/api/v1/login/', 
            dataLogin, format='json'
        )
        middleware = SessionMiddleware()
        middleware.process_request(request_login)
        request_login.session.save()
        force_authenticate(request_login, dataLogin)
        response_login = user_view_login(request_login)

        if response_login.status_code == status.HTTP_200_OK:
            pass
        else:
            raise Exception(
                "Error occurred during login to test user!")

        return response_login

    def Perform_Test(self, dataLogin, dataPasswordChange):

        response_login = self.Perform_Login(dataLogin)

        factory_official = APIRequestFactory()
        user_view_official = ChangePasswordView.as_view()
        theURL = "http://127.0.0.1:8000/api/v1/change-password/"

        request_official = factory_official.post(
            theURL, dataPasswordChange, format='json',
            HTTP_AUTHORIZATION=f"Bearer {response_login.data['access']}")
        response_official = user_view_official(request_official)

        return response_official

    def test_user_changepassword(self):
        response_changepassword = self.Perform_Test(
            self.user_payload_toLoginOldPass, self.user_payload_changePass)
        self.assertEqual(response_changepassword.status_code,
                         status.HTTP_200_OK)

        response_loginToNewPassword = self.Perform_Login(
            self.user_payload_toLoginNewPass)
        self.assertEqual(
            response_loginToNewPassword.status_code, status.HTTP_200_OK)


class test_case_core_api(APITestCase):

    @classmethod
    def setUpTestData(self):
        self.register_url = 'http://127.0.0.1:8000/api/v1/register/'
        self.login_url = 'http://127.0.0.1:8000/api/v1/login/'
        self.repository_url = 'http://127.0.0.1:8000/api/v1/repos/'
        self.branch_url = 'http://127.0.0.1:8000/api/v1/branches/'
        self.commit_url = 'http://127.0.0.1:8000/api/v1/commits/'

        self.valid_user_payload = {
            "username": "test_case_user_repo_creation",
            "email": "test_case_user_repo_creation@email.com",
            "password": "password",
            "password2": "password"
        }

        # Register the testing user
        factory = APIRequestFactory()
        request = factory.post(
            self.register_url, self.valid_user_payload, format='json')
        user_view = RegistrationView.as_view()
        response = user_view(request)
        print(response.status_code)
        if response.status_code != 201:
            raise Exception("Couldn't create the repository test user!")
        created_user = User.objects.order_by('?')[0]

        # Logging into the user
        self.dataLogin = {
            "email": f"{created_user.email}",
            "password": "password"
        }

        factory_login = APIRequestFactory()
        user_view_login = LoginView.as_view()

        request_login = factory_login.post(
            self.login_url, self.dataLogin, format='json')
        middleware = SessionMiddleware()
        middleware.process_request(request_login)
        request_login.session.save()
        force_authenticate(request_login, self.dataLogin)
        response_login = user_view_login(request_login)

        if not response_login.status_code == status.HTTP_200_OK:
            raise Exception(f"Error occurred during login to test user!")

        self.authorization_header = f"Bearer {response_login.data['access']}"
        self.create_user_id = created_user.id

        # Create a test repository
        self.test_repository_data = {
            "name": "test_repo",
            "owner": self.create_user_id,
        }
        factory = APIRequestFactory()
        view = RepositoryList.as_view()
        request = factory.post(
            self.repository_url, 
            self.test_repository_data, 
            format='json',
            HTTP_AUTHORIZATION=self.authorization_header
        )
        response = view(request)
        self.created_repo = Repository.objects.order_by('?')[0]

        # Create test branch
        self.test_branch_data = {
            "name": "test_branch",
            "repo": self.created_repo.id,
        }
        view = BranchList.as_view()
        request = factory.post(
            self.branch_url,
            self.test_branch_data, 
            format='json',
            HTTP_AUTHORIZATION=self.authorization_header
        )
        response = view(request)
        self.created_branch= Branch.objects.order_by('?')[0]

         # Create test commit
        self.test_commit_data = {
            "message" : "test commit message",
            "branch" : self.created_branch.id,
            "committer" : self.create_user_id,
            "unique_id" : "us34ids3472832k3423jh4234k2j34g2",
        }
        view = CommitList.as_view()
        request = factory.post(
            self.commit_url,
            self.test_commit_data,
            format='json',
            HTTP_AUTHORIZATION=self.authorization_header
        )
        response = view(request)
        self.created_commit= Commit.objects.order_by('?')[0]

        ## Test data
        # Repository test data
        self.valid_repository_payload = {
            "name": "test_repo_1",
            "private": True,
            "owner": self.create_user_id,
        }

        self.empty_name_repository_payload = {
            "name": "",
            "owner": self.create_user_id,
        }

        self.edit_name_repository_payload = {
            "name": "new_name",
            "owner": self.create_user_id,
        }

        # Branch test data
        self.valid_branch_payload = {
            "name": "test_branch_1",
            "repo": self.created_repo.id,
        }

        self.empty_name_branch_payload = {
            "name": "",
            "repo": self.created_repo.id,
        }

        self.edit_name_branch_payload = {
            "name": "test_branch_1_new_name",
            "repo": self.created_repo.id,
        }

        # Commit test data
        self.valid_commit_payload = {
            "message" : "test commit message",
            "branch" : self.created_branch.id,
            "committer" : self.create_user_id,
            "unique_id" : "us34ids3472832k3423jh423456j34g2",
        }

        self.not_valid_commit_payload = {
            "message" : "test commit message",
            "branch" : 1234567,
            "committer" : self.create_user_id,
            "unique_id" : "",
        }

        self.edit_commit_message_payload = {
            "message" : "new test commit message",
            "branch" : self.created_branch.id,
            "committer" : self.create_user_id,
            "unique_id" : "us34ids3472832k3423jh423456j34g2",
        }

    @classmethod
    def tearDownClass(self):
        user_folder = "/home/mvcs/test_case_user_repo_creation"
        try:
            shutil.rmtree(user_folder)
        except:
            print(f"Couldn't delete {user_folder}!")

    def perform_test(self, data, url, request_type, view, pk=None):
        factory = APIRequestFactory()
        if request_type == "POST":
            request = factory.post(
                url, data, format='json',
                HTTP_AUTHORIZATION=self.authorization_header
            )
        elif request_type == "PUT":
            request = factory.put(
                url, data, format='json',
                HTTP_AUTHORIZATION=self.authorization_header
            )
        elif request_type == "DELETE":
            request = factory.delete(
                url, HTTP_AUTHORIZATION=self.authorization_header)

        if pk is not None:
            response = view(request, pk)
        else:
            response = view(request)

        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        response.render()

        return response

    # Repository test cases
    def test_create_valid_repository(self):
        response = self.perform_test(
            self.valid_repository_payload, 
            self.repository_url, 
            "POST",
            RepositoryList.as_view()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_repository_with_empty_name(self):
        response = self.perform_test(
            self.empty_name_repository_payload, 
            self.repository_url, 
            "POST",
            RepositoryList.as_view()
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_repository_name(self):
        response = self.perform_test(
            self.edit_name_repository_payload, 
            self.repository_url + f"{self.created_repo.id}", 
            "PUT",
            RepositoryDetail.as_view(),
            pk=self.created_repo.id
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Branch test cases
    def test_create_valid_branch(self):
        response = self.perform_test(
            self.valid_branch_payload, 
            self.branch_url, 
            "POST",
            BranchList.as_view()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_branch_with_empty_name(self):
        response = self.perform_test(
            self.empty_name_branch_payload, 
            self.branch_url, 
            "POST",
            BranchList.as_view()
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_branch_name(self):
        response = self.perform_test(
            self.edit_name_branch_payload, 
            self.branch_url + f"{self.created_branch.id}", 
            "PUT",
            BranchDetail.as_view(),
            pk=self.created_branch.id
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Commit test cases
    def test_create_valid_commit(self):
        response = self.perform_test(
            self.valid_commit_payload, 
            self.commit_url, 
            "POST",
            CommitList.as_view()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_commit_non_valid_data(self):
        response = self.perform_test(
            self.not_valid_commit_payload,
            self.commit_url, 
            "POST",
            CommitList.as_view()
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_commit_message(self):
        response = self.perform_test(
            self.edit_commit_message_payload, 
            self.commit_url + f"{self.created_commit.id}", 
            "PUT",
            CommitDetail.as_view(),
            pk=self.created_commit.id
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # Delete operations test cases
    def test_delete_project(self):
        # Delete commit
        response = self.perform_test(
            {}, 
            self.commit_url + f"{self.created_commit.id}", 
            "DELETE",
            CommitDetail.as_view(),
            pk=self.created_commit.id
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Delete branch
        response = self.perform_test(
            {}, 
            self.branch_url + f"{self.created_branch.id}", 
            "DELETE",
            BranchDetail.as_view(),
            pk=self.created_branch.id
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Delete repo
        response = self.perform_test(
            {}, 
            self.repository_url + f"{self.created_repo.id}", 
            "DELETE",
            RepositoryDetail.as_view(),
            pk=self.created_repo.id
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
