# Generated by Django 5.0.6 on 2024-10-08 23:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contratos', '0007_alter_cotizacion_comentario'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cotizacion',
            name='comentario',
        ),
    ]