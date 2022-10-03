from django.urls import path

from . import views 

# /api/products/
urlpatterns = [
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),

    path('repos/', views.RepositoryList.as_view()),
    path('repos/<int:pk>/', views.RepositoryDetail.as_view()),

    path('branches/', views.BranchList.as_view()),
    path('branches/<int:pk>/', views.BranchDetail.as_view()),
    
    path('commits/', views.CommitList.as_view()),
    path('commits/<int:pk>/', views.CommitDetail.as_view()),
]

