# Generated by Django 5.0.7 on 2024-08-12 13:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_profile_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='date_of_birth',
            new_name='birth_date',
        ),
    ]
