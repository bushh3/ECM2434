# Generated by Django 5.1.6 on 2025-03-24 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_playerbadge_badge_remove_diycreation_player_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
