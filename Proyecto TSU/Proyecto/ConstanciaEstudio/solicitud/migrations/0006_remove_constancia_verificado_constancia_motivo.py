# Generated by Django 5.0 on 2024-08-29 22:17

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solicitud', '0005_remove_constancia_motivo_constancia_verificado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='constancia',
            name='verificado',
        ),
        migrations.AddField(
            model_name='constancia',
            name='motivo',
            field=models.TextField(default=django.utils.timezone.now, verbose_name='Motivo de la Solicitud'),
            preserve_default=False,
        ),
    ]
