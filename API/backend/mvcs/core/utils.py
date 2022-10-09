from rest_framework_simplejwt.tokens import RefreshToken
from .models import Repository, Branch, Commit, User
from .serializers import RepositorySerializer, BranchSerializer, CommitSerializer, UserSerializer

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_repo_details(id):
    repo = Repository.objects.get(pk=id)
    repo_data = RepositorySerializer(repo).data

    owner = User.objects.get(pk=repo_data['id'])
    repo_data['owner_data'] = UserSerializer(owner).data

    branches = Branch.objects.filter(repo=id)
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
    