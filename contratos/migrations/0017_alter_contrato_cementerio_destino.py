# Generated by Django 5.0.6 on 2024-11-03 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contratos', '0016_alter_contrato_sala_velatorio_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contrato',
            name='cementerio_destino',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
