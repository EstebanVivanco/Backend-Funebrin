# Generated by Django 5.0.6 on 2024-10-20 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contratos', '0012_exhumacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='exhumacion',
            name='valor_servicio',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
