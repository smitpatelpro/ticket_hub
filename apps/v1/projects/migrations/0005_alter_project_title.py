# Generated by Django 5.2 on 2025-04-24 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_project_description_project_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='title',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
