# Generated by Django 5.1 on 2024-10-13 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0010_alter_quiz_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='current_question',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
