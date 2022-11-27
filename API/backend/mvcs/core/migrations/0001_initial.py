from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('username', models.CharField(max_length=70, unique=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('linkedin_token', models.TextField(blank=True, default='')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='date joined')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='last login')),
                ('first_name', models.CharField(max_length=60, null=True)),
                ('last_name', models.CharField(max_length=60, null=True)),
                ('bio', models.TextField(blank=True, max_length=2000, null=True)),
                ('date_of_birth', models.DateTimeField(null=True, verbose_name='date of birth')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='image')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('has_locked_files', models.BooleanField(default=False)),
                ('locked', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('private', models.BooleanField(default=False)),
                ('contributors', models.ManyToManyField(null=True, related_name='repo_contributors', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Commit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('message', models.TextField(max_length=1500)),
                ('unique_id', models.CharField(max_length=64, unique=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.branch')),
                ('committer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='branch',
            name='repo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.repository'),
        ),
    ]
