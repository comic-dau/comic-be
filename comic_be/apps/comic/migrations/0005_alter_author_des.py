# Generated by Django 5.1.6 on 2025-03-18 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comic', '0004_history_comic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='des',
            field=models.TextField(null=True),
        ),
    ]
