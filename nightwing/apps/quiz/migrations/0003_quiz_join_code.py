# Generated by Django 5.1 on 2024-08-30 16:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_multiplechoicequestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='join_code',
            field=models.IntegerField(null=True, unique=True, validators=[django.core.validators.MinValueValidator(100000), django.core.validators.MaxValueValidator(999999)]),
        ),
    ]