# Generated by Django 5.1.2 on 2024-10-28 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SEP', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='name',
        ),
    ]
