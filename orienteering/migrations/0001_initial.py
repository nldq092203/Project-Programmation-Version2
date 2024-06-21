# Generated by Django 5.0.6 on 2024-06-21 08:12

import datetime
import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('longitude', models.FloatField()),
                ('latitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='RaceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('rule', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=150, unique=True)),
                ('department', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, null=True, upload_to='profile_images')),
                ('role', models.CharField(choices=[('Coach', 'Coach'), ('Runner', 'Runner')], max_length=10)),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_user_group', to='auth.group')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permission', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_user_permission', to='auth.permission')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='GroupRunner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('department', models.CharField(max_length=50)),
                ('members', models.ManyToManyField(blank=True, null=True, related_name='member_group_runners', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('publish', models.BooleanField(default=False)),
                ('subtitle', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='event_images')),
                ('department', models.CharField(blank=True, max_length=100, null=True)),
                ('is_finished', models.BooleanField(default=False)),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to=settings.AUTH_USER_MODEL)),
                ('group_runner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='orienteering.grouprunner')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='orienteering.location')),
            ],
        ),
        migrations.CreateModel(
            name='Race',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('time_limit', models.DurationField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='races', to='orienteering.event')),
                ('race_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='races', to='orienteering.racetype')),
            ],
        ),
        migrations.CreateModel(
            name='CheckPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('longitude', models.FloatField()),
                ('latitude', models.FloatField()),
                ('score', models.IntegerField(blank=True, default=0, null=True)),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkpoints', to='orienteering.race')),
            ],
        ),
        migrations.CreateModel(
            name='RaceRunner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_time', models.DurationField(blank=True, default=datetime.timedelta(0), null=True)),
                ('score', models.IntegerField(blank=True, default=0, null=True)),
                ('is_finished', models.BooleanField(default=False)),
                ('correct_checkpoints', models.JSONField(blank=True, null=True)),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='race_runners', to='orienteering.race')),
                ('runner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='race_runners', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CheckPointRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('longitude', models.FloatField()),
                ('latitude', models.FloatField()),
                ('is_correct', models.BooleanField(blank=True, default=False, null=True)),
                ('race_runner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkpoint_records', to='orienteering.racerunner')),
            ],
        ),
    ]
