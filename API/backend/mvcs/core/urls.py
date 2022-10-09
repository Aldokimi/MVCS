from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from . import views 

# /api/products/
urlpatterns = [
    # Authentication URLs
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('token-refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    # Models URLs
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),

    path('repos/', views.RepositoryList.as_view()),
    path('repos/<int:pk>/', views.RepositoryDetail.as_view()),
    path('repos/data/<int:pk>/', views.RepositoryDataDetail.as_view()),

    path('branches/', views.BranchList.as_view()),
    path('branches/<int:pk>/', views.BranchDetail.as_view()),
    
    path('commits/', views.CommitList.as_view()),
    path('commits/<int:pk>/', views.CommitDetail.as_view()),
]

