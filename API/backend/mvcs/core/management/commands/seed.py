import lzma
import os
import random
import shutil
import tarfile
import uuid
import warnings

from django.db import transaction
from django.core.management.base import BaseCommand

from ...serializers import CreateBranchSerializer, CreateCommitSerializer

from ...models import User, Repository, Branch, Commit
from ...tests.factories import UserFactory, RepositoryFactory, BranchFactory, CommitFactory

NUM_OF_FAKE_USERS = 5
NUM_OF_FAKE_REPOSITORIES = 10
NUM_OF_FAKE_BRANCHES = 20
NUM_OF_FAKE_COMMITS = 50


class Command(BaseCommand):
    def __init__(self) -> None:
        warnings.filterwarnings("ignore")
        super().__init__()
    help = "Generates test data"

    def get_last_commit(self, branch_id):
        commits = Commit.objects.filter(branch=branch_id)
        latest_commit = commits.first()
        for commit in commits:
            if commit.date_created > latest_commit.date_created:
                latest_commit = commit
        return latest_commit

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        models = [User, Repository, Branch, Commit]
        for user in User.objects.all():
            if os.path.isdir('/home/mvcs/' + user.username + '/'):
                shutil.rmtree('/home/mvcs/' + user.username + '/')
        for m in models:
            m.objects.all().delete()

        self.stdout.write("Creating new data...")

        # Create all the users
        people = []
        for _ in range(NUM_OF_FAKE_USERS):
            person = UserFactory()
            path = os.path.join("/home/mvcs/", person.username + '/')
            os.mkdir(path)
            os.system(f"chown -R mvcs:mvcs {path}")
            person.set_password('password')
            person.save()
            people.append(person)
        self.stdout.write(self.style.SUCCESS(
            'Successfully seeded fake USERS into the database'))

        # Create repositories and add users to them
        repos = []
        for _ in range(NUM_OF_FAKE_REPOSITORIES):
            owner = random.choice(people)
            contr = random.sample(people, 3)
            repo = RepositoryFactory.create(
                owner=owner, 
                contributors=(contr[0], contr[1], contr[2])
            )
            path = os.path.join(
                "/home/mvcs/" + repo.owner.username + '/', repo.name)
            os.mkdir(path)
            os.system(f"chown -R mvcs:mvcs {path}")

            # Create a new branch called main which have a commit inside it
            # Create the main branch
            branch_request_data = {
                "repo": repo.id,
                "name": "main",
            }

            branch_data = CreateBranchSerializer(data=branch_request_data)
            if branch_data.is_valid():
                branch_data.save()
                path_to_branch = os.path.join(
                    "/home/mvcs/" + repo.owner.username + '/' + repo.name,
                    branch_data.validated_data['name'])
                os.mkdir(path_to_branch)
                os.system(f"chown -R mvcs:mvcs {path_to_branch}")
            else:
                os.rmdir(path)
                os.system(f"chown -R mvcs:mvcs {path}")
                raise Exception("Couldn't create main branch in repo!")

            try:
                branch = Branch.objects.get(
                    pk=branch_data.data['id'], name=branch_data.validated_data['name'])
            except Branch.DoesNotExist:
                raise Exception("Couldn't get the main branch!")

            # Create the first commit in the main branch
            commit_request_data = {
                "message": 'Initial commit',
                "branch": branch.id,
                "committer": repo.owner.id,
                "unique_id": uuid.uuid4().hex
            }

            commit_data = CreateCommitSerializer(data=commit_request_data)
            if commit_data.is_valid():
                commit_data.save()
            else:
                os.rmdir(path)
                raise Exception(
                    "Couldn't create initial commit in the main branch in repo!")

            # Create the compressed folder of the initial commit
            base_path = "/home/mvcs/" + repo.owner.username + '/' + repo.name + '/' + 'main'
            commit_unique_id = commit_data.validated_data['unique_id']
            commit_file_name = f'{commit_unique_id}.tar.xz'
            xz_file = lzma.LZMAFile(commit_file_name, mode='w')
            with tarfile.open(mode='w', fileobj=xz_file) as tar_xz_file:
                for file in os.listdir(base_path):
                    tar_xz_file.add(os.path.join(base_path, file))
            xz_file.close()
            shutil.copy2(commit_file_name, base_path)
            os.system(
                f"chown -R mvcs:mvcs {os.path.join(base_path, commit_file_name)}")
            os.remove(commit_file_name)
            repos.append(repo)
        self.stdout.write(self.style.SUCCESS(
            'Successfully seeded fake REPOSITORIES into the database'))

        # Create branches and add repos to them
        branches = []
        for _ in range(NUM_OF_FAKE_BRANCHES):
            repo = random.choice(repos)
            branch = BranchFactory(repo=repo)
            path = os.path.join(
                "/home/mvcs/" + repo.owner.username + '/' + repo.name,
                branch.name)
            os.mkdir(path)
            os.system(f"chown -R mvcs:mvcs {path}")

            # Get the main branch of the repo
            branches_with_main = Branch.objects.filter(repo=branch.repo, name="main")
            main_branch = branches_with_main.first()
            last_commit = self.get_last_commit(main_branch.id)

            # Copy the last commit from the main branch
            base_path = "/home/mvcs/" +\
                repo.owner.username + '/' + repo.name + '/' + branch.name
            main_branch_dir = "/home/mvcs/" +\
                repo.owner.username + '/' + repo.name + '/' + "main"
            commit_file_name = f'{last_commit.unique_id}.tar.xz'

            shutil.copy(os.path.join(main_branch_dir,
                        commit_file_name), base_path)
            os.system(
                f"chown -R mvcs:mvcs {os.path.join(base_path, commit_file_name)}")
            branches.append(branch)
        self.stdout.write(self.style.SUCCESS(
            'Successfully seeded fake BRANCHES into the database'))

        # Create branches and add repos to them
        for _ in range(NUM_OF_FAKE_COMMITS):
            branch = random.choice(branches)
            committer = random.choice(people)
            CommitFactory(branch=branch, committer=committer)
        self.stdout.write(self.style.SUCCESS(
            'Successfully seeded fake COMMITS into the database'))

        self.stdout.write(self.style.SUCCESS(
            '\nSEEDING IS DONE SUCCESSFULLY\n'))
