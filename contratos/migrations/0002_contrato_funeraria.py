# Generated by Django 5.0.6 on 2024-09-15 20:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('contratos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contrato',
            name='funeraria',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='accounts.funeraria'),
            preserve_default=False,
        ),
    ]
