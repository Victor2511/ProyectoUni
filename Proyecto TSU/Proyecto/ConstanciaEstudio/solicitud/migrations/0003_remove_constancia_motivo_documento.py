# Generated by Django 5.0 on 2024-08-29 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('solicitud', '0002_constancia_motivo_documento'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='constancia',
            name='motivo_documento',
        ),
    ]
