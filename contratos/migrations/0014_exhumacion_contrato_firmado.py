# Generated by Django 5.0.6 on 2024-10-20 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contratos', '0013_exhumacion_valor_servicio'),
    ]

    operations = [
        migrations.AddField(
            model_name='exhumacion',
            name='contrato_firmado',
            field=models.DateField(blank=True, null=True),
        ),
    ]
