# Generated by Django 5.0.6 on 2024-11-17 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_user_banco_user_numero_cuenta_liquidacionsueldo'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='tipo_cuenta',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
