from io import StringIO
import random
from typing import Optional
import warnings

from django.db import transaction
from django.core.management.base import BaseCommand

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

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        models = [User, Repository, Branch, Commit]
        for m in models:
            m.objects.all().delete()

        self.stdout.write("Creating new data...")
        # Create all the users
        people = []
        for _ in range(NUM_OF_FAKE_USERS):
            person = UserFactory()
            people.append(person)
        self.stdout.write(self.style.SUCCESS('Successfully seeded fake USERS into the database'))

        # Create repositories and add users to them
        repos = []
        for _ in range(NUM_OF_FAKE_REPOSITORIES):
            owner = random.choice(people)
            contr = random.choice(people)
            repo = RepositoryFactory(owner=owner, contributors=contr)
            repos.append(repo)
        self.stdout.write(self.style.SUCCESS('Successfully seeded fake REPOSITORIES into the database'))

        # Create branches and add repos to them
        branches = []
        for _ in range(NUM_OF_FAKE_BRANCHES):
            repo = random.choice(repos)
            branch = BranchFactory(repo=repo)
            branches.append(branch)
        self.stdout.write(self.style.SUCCESS('Successfully seeded fake BRANCHES into the database'))
        
        # Create branches and add repos to them
        for _ in range(NUM_OF_FAKE_COMMITS):
            branch = random.choice(branches)
            committer = random.choice(people)
            CommitFactory(branch=branch, committer=committer)
        self.stdout.write(self.style.SUCCESS('Successfully seeded fake COMMITS into the database'))
        
        self.stdout.write(self.style.SUCCESS('\nSEEDING IS DONE SUCCESSFULLY\n'))