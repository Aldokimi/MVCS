from django.http import Http404
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Repository, Branch, Commit, User
from .serializers import RepositorySerializer, BranchSerializer, CommitSerializer, UserSerializer

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_repo_details(repo_id, owner_id):
    try:
        repo = Repository.objects.get(pk=repo_id)
        repo_data = RepositorySerializer(repo).data
    except Repository.DoesNotExist:
        raise Http404
    
    try:
        owner = User.objects.get(pk=owner_id)
        repo_data['owner_data'] = UserSerializer(owner).data
    except Repository.DoesNotExist:
        raise Http404

    branches = Branch.objects.filter(repo=repo.id)
    branches_array = {}
    
    for branch in branches:
        branch_data = BranchSerializer(branch).data

        commits = Commit.objects.filter(branch=branch)
        commit_array = {}
        for commit in commits:
            commit_data = CommitSerializer(commit).data
            commit_array[commit_data['id']] = commit_data

        branch_data['commits'] = commit_array
        branches_array[branch_data['id']] = branch_data

    repo_data['branches'] = branches_array

    return repo_data


def get_user_repositories(user_id):
    repos = Repository.objects.filter(owner=user_id)
    return repos

def get_repo_branches(repo_id):
    branches = Branch.objects.filter(repo=repo_id)
    return branches

def get_branches_commits(branch_id):
    commits = Commit.objects.filter(branch=branch_id)
    return commits
