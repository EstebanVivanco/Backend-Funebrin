# Generated by Django 5.0.6 on 2024-11-03 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contratos', '0017_alter_contrato_cementerio_destino'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contrato',
            name='fecha_fin_velatorio',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='contrato',
            name='fecha_inicio_velatorio',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
