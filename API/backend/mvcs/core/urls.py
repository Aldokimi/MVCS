from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from core import urls
from rest_framework_simplejwt import views as jwt_views

from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="MVCS API",
        default_version='v1',
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    url="http://localhost:8000/api/v1/",
    public=True,
    permission_classes=[permissions.AllowAny],
)


# /api/products/
urlpatterns = [
    # API Docs
    re_path(r'^endpoints(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^endpoints/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^docs/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Authentication URLs
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('change-password/', views.ChangePasswordView.as_view(),
         name='change_password'),
    path('token-refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    # Models URLs
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('users/<int:pk>/repos/', views.UserRepositories.as_view()),
    path('users/<int:pk>/branches/', views.UserBranches.as_view()),
    path('users/<int:pk>/commits/', views.UserCommits.as_view()),


    path('repos/', views.RepositoryList.as_view()),
    path('repos/<int:pk>/', views.RepositoryDetail.as_view()),
    path('repos/data/<str:owner>/<str:name>/',
         views.RepositoryDataDetail.as_view()),

    path('branches/', views.BranchList.as_view()),
    path('branches/<int:pk>/', views.BranchDetail.as_view()),

    path('commits/', views.CommitList.as_view()),
    path('commits/<int:pk>/', views.CommitDetail.as_view()),
]
