# Generated by Django 5.1 on 2024-08-30 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0004_merge_20240830_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='started',
            field=models.BooleanField(default=False),
        ),
    ]
