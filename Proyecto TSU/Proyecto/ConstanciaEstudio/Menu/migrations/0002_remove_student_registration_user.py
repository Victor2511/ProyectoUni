# Generated by Django 5.0 on 2024-08-21 21:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Menu', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student_registration',
            name='user',
        ),
    ]
