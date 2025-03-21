# Generated by Django 5.1.6 on 2025-03-02 20:32

import django.contrib.auth.models
import django.contrib.auth.validators
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
            name='Badge',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('criteria', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='DIYCreation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo_location', models.CharField(max_length=50)),
                ('title', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField()),
                ('approved', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('criteria', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
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
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.diycreation')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.player')),
            ],
        ),
        migrations.AddField(
            model_name='diycreation',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.player'),
        ),
        migrations.CreateModel(
            name='PlayerBadge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.badge')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.player')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=500)),
                ('option1', models.CharField(default='Default Option 1', max_length=100)),
                ('option2', models.CharField(default='Default Option 2', max_length=100)),
                ('option3', models.CharField(default='Default Option 3', max_length=100)),
                ('option4', models.CharField(default='Default Option 4', max_length=100)),
                ('correct_option', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], default='A', max_length=1)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='core.quiz')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerQuiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('timestamp', models.DateTimeField()),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.player')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.quiz')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('times_completed', models.IntegerField(default=0)),
                ('last_completed', models.DateTimeField()),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.player')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.task')),
            ],
        ),
        migrations.CreateModel(
            name='WalkingData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('distance', models.FloatField()),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.player')),
            ],
        ),
    ]
