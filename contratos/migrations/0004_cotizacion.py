# Generated by Django 5.0.6 on 2024-10-06 21:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_servicio_url_imagen'),
        ('contratos', '0003_fallecido_certificado_autorizacion_sepultacion_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cotizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_cliente', models.CharField(max_length=255)),
                ('email_cliente', models.EmailField(max_length=254)),
                ('telefono_cliente', models.CharField(max_length=20)),
                ('descripcion', models.TextField()),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')], default='pendiente', max_length=50)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('funeraria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.funeraria')),
                ('servicios', models.ManyToManyField(related_name='cotizaciones', to='accounts.servicio')),
            ],
        ),
    ]