# Generated by Django 5.2 on 2025-04-24 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_alter_projectinvitation_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmembership',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20),
        ),
    ]
