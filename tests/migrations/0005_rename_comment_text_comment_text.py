# Generated by Django 5.0.7 on 2024-08-09 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0004_rename_questions_count_result_question_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='comment_text',
            new_name='text',
        ),
    ]
