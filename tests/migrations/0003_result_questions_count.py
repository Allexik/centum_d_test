# Generated by Django 5.0.7 on 2024-08-09 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0002_rename_usertest_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='questions_count',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]
