# Generated by Django 5.1.6 on 2025-03-21 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_recyclingbin_scanrecord'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='scanrecord',
            unique_together={('user', 'scan_date', 'qr_code')},
        ),
    ]
