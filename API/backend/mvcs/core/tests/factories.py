import factory
from factory.django import DjangoModelFactory
from ..models import User, Repository,  Branch, Commit

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Faker('name')
    email = factory.Faker('email')
    date_of_birth = factory.Faker('date_time')
    is_active = factory.Faker('pybool')
    is_admin = factory.Faker('pybool')
    linkedin_token = factory.Faker('uuid4')
    date_joined = factory.Faker('date_time')
    last_login  = factory.Faker('date_time')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    bio = factory.Faker('sentence')
    date_of_birth =factory.Faker('date_time')
    profile_picture = factory.Faker('image_url')
    password = factory.PostGenerationMethodCall('set_password','password')

class RepositoryFactory(DjangoModelFactory):
    class Meta:
        model = Repository

    name = factory.Faker('name')
    date_created = factory.Faker('date_time')
    last_updated = factory.Faker('date_time')
    private = factory.Faker('pybool')
    contributors = factory.Faker(UserFactory)
    owner = factory.Faker(UserFactory)

class BranchFactory(DjangoModelFactory):
    class Meta:
        model = Branch

    repo = factory.Faker(RepositoryFactory)
    name = factory.Faker('name')
    date_created = factory.Faker('date_time')
    has_locked_files = factory.Faker('pybool')
    locked = factory.Faker('pybool')

class CommitFactory(DjangoModelFactory):
    class Meta:
        model = Commit

    date_created = factory.Faker('date_time')
    date_updated =factory.Faker('date_time')
    message = factory.Faker('sentence')
    branch = factory.Faker(BranchFactory)
    committer = factory.Faker(UserFactory)
    unique_id = factory.Faker('uuid4')